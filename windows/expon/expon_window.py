import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, pyqtSignal
from PyQt6.QtGui import QIntValidator, QValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog
)

from windows.expon.expon_plot import ExponDensityPlot, ExponPlot, ExponReliabilityPlot
import scipy.stats as stats

from decimal import Decimal


class FocusOutLineEdit(QLineEdit):
    # Сигнал, который будет испускаться при потере фокуса
    focusLost = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def focusOutEvent(self, event: QEvent):
        # Вызываем сигнал при потере фокуса
        self.focusLost.emit()
        super().focusOutEvent(event)


class ExponWindow(QWidget):

    inputs_validated = pyqtSignal(bool)

    time_changed = pyqtSignal()
    f_t_changed = pyqtSignal(object)
    reliability_changed = pyqtSignal(object)

    time_for_reliability_changed = pyqtSignal(object)

    replacement_time_changed = pyqtSignal(object)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Экспоненциальное распределение")
        self.resize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Параметры
        self.lambda_value = None  # Интенсивность отказа

        self.time = None
        self.f_t = None           # Вероятность отказа
        self.reliability = None   # Вероятность безотказной работы

        self.reliability_level = None
        self.time_for_reliability = None

        self.max_failure_probability = None
        self.replacement_time = None

        self.check = False

        # Основной макет
        layout = QVBoxLayout(self)
        self.setLayout(layout)


        self.lambda_value_label = QLabel("Интенсивность отказов (λ):")
        self.lambda_value_input = FocusOutLineEdit()
        self.lambda_value_input.setPlaceholderText("Введите интенсивность отказов")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.lambda_value_input.setValidator(double_validator)
        layout.addWidget(self.lambda_value_label)
        layout.addWidget(self.lambda_value_input)
        self.lambda_value_input.textChanged.connect(lambda _ : self.validate_number(self.lambda_value_input))
        self.lambda_value_input.textChanged.connect(lambda _: self.validate_inputs())

        self.plot_distribution_density_btn = QPushButton("Построить график плотности распределения")
        layout.addWidget(self.plot_distribution_density_btn)
        self.plot_distribution_density_btn.clicked.connect(self.plot_distribution_density)
        self.inputs_validated.connect(self.plot_distribution_density_btn.setEnabled)
        self.plot_distribution_density_btn.setEnabled(False)


        self.plot_distribution_btn = QPushButton("Построить график распределения")
        layout.addWidget(self.plot_distribution_btn)
        self.plot_distribution_btn.clicked.connect(self.plot_distribution)
        self.inputs_validated.connect(self.plot_distribution_btn.setEnabled)
        self.plot_distribution_btn.setEnabled(False)


        self.plot_reliability_btn = QPushButton("Построить график вероятности безотказной работы")
        layout.addWidget(self.plot_reliability_btn)
        self.plot_reliability_btn.clicked.connect(self.plot_reliability)
        self.inputs_validated.connect(self.plot_reliability_btn.setEnabled)
        self.plot_reliability_btn.setEnabled(False)


        self.time_label = QLabel("Время (t):")
        self.time_input = FocusOutLineEdit()
        self.time_input.setPlaceholderText("Введите время")
        regex = QRegularExpression(r"^\d*(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.time_input.setValidator(double_validator)
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_input)
        self.time_input.textChanged.connect(lambda _ : self.set_time())

        self.inputs_validated.connect(lambda _: self.calculate_with_time())

        self.f_label = QLabel("Вероятность безотказной работы до времени t (R(t)):")
        self.f_input = QLineEdit()
        self.f_input.setReadOnly(True)
        layout.addWidget(self.f_label)
        layout.addWidget(self.f_input)
        self.f_t_changed.connect(lambda value: self.f_input.setText(str(value))
                                        if value is not None
                                        else self.f_input.setText(""))

        self.reliability_label = QLabel("Вероятность безотказной работы (R(t)):")
        self.reliability_input = QLineEdit()
        self.reliability_input.setReadOnly(True)
        layout.addWidget(self.reliability_label)
        layout.addWidget(self.reliability_input)
        self.reliability_changed.connect(lambda value: self.reliability_input.setText(str(value))
                                                if value is not None
                                                else self.reliability_input.setText(""))



        self.reliability_level_label_title = QLabel("Определение времени наработки на отказ")
        self.reliability_level_label = QLabel("Надежность:")
        self.reliability_level_input = FocusOutLineEdit()
        self.reliability_level_input.setPlaceholderText("Введите надежность")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.reliability_level_input.setValidator(double_validator)
        layout.addWidget(self.reliability_level_label_title)
        layout.addWidget(self.reliability_level_label)
        layout.addWidget(self.reliability_level_input)
        self.reliability_level_input.textChanged.connect(lambda _ : self.set_reliability_level())

        self.time_for_reliability_label = QLabel("Время наработки на отказ:")
        self.time_for_reliability_input = QLineEdit()
        self.time_for_reliability_input.setReadOnly(True)
        layout.addWidget(self.time_for_reliability_label)
        layout.addWidget(self.time_for_reliability_input)
        self.time_for_reliability_changed.connect(lambda value: self.time_for_reliability_input.setText(str(value))
                                                if value is not None
                                                else self.time_for_reliability_input.setText(""))

        self.inputs_validated.connect(lambda _: self.calculate_time_for_reliability())



        self.max_failure_probability_label_title = QLabel("Рассчитать минимальное время до замены")
        self.max_failure_probability_label = QLabel("Вероятность отказа:")
        self.max_failure_probability_input = FocusOutLineEdit()
        self.max_failure_probability_input.setPlaceholderText("Введите вероятность отказа")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.max_failure_probability_input.setValidator(double_validator)
        layout.addWidget(self.max_failure_probability_label_title)
        layout.addWidget(self.max_failure_probability_label)
        layout.addWidget(self.max_failure_probability_input)
        self.max_failure_probability_input.textChanged.connect(lambda _ : self.set_max_failure_probability())

        self.replacement_time_label = QLabel("Минимальное время замены:")
        self.replacement_time_input = QLineEdit()
        self.replacement_time_input.setReadOnly(True)
        layout.addWidget(self.replacement_time_label)
        layout.addWidget(self.replacement_time_input)
        self.replacement_time_changed.connect(lambda value: self.replacement_time_input.setText(str(value))
                                                if value is not None
                                                else self.replacement_time_input.setText(""))

        self.inputs_validated.connect(lambda _: self.calculate_replacement_time())

        self.export_btn = QPushButton("Экспортировать данные")
        layout.addWidget(self.export_btn)
        self.export_btn.clicked.connect(self.export_data)
        self.inputs_validated.connect(self.export_btn.setEnabled)
        self.export_btn.setEnabled(False)

    def validate_number(self, input_num: QLineEdit):
        if input_num.text() == "":
            input_num.setStyleSheet("color: black;")
            return False

        text = input_num.text()
        check = input_num.validator().validate(text, 0)[0]
        if check != QValidator.State.Acceptable:
            input_num.setStyleSheet("color: red;")
            return False

        input_num.setStyleSheet("color: black;")
        return True


    def calculate_with_time(self):
        if (self.time is None) or (not self.check):
            self.f_t = None
            self.reliability = None
        else:
            self.f_t = stats.expon.pdf(float(self.time), scale=float(1 / self.lambda_value))
            self.reliability = 1 - stats.expon.cdf(float(self.time), scale=float(1 / self.lambda_value))

        self.f_t_changed.emit(self.f_t)
        self.reliability_changed.emit(self.reliability)

    def calculate_time_for_reliability(self):
        if (self.reliability_level is None) or (not self.check):
            self.time_for_reliability = None
        else:
            self.time_for_reliability = stats.expon.ppf(float(1 - self.reliability_level), scale=float(1 / self.lambda_value))

        self.time_for_reliability_changed.emit(self.time_for_reliability)

    def calculate_replacement_time(self):
        if (self.max_failure_probability is None) or (not self.check):
            self.replacement_time = None
        else:
            self.replacement_time = stats.expon.ppf(float(self.max_failure_probability), scale=float(1 / self.lambda_value))

        self.replacement_time_changed.emit(self.replacement_time)


    def validate_inputs(self):
        self.check = True
        if not self.validate_number(self.lambda_value_input):
            self.check = False

        if self.check:
            self.set_values()

        self.inputs_validated.emit(self.check)

        return self.check

    def set_values(self):

        self.lambda_value = Decimal(self.lambda_value_input.text())

    def plot_distribution_density(self):
        self.plot_density_window = ExponDensityPlot(self.lambda_value)
        self.plot_density_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_density_window.show()

    def plot_distribution(self):
        self.plot_window = ExponPlot(self.lambda_value)
        self.plot_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_window.show()

    def plot_reliability(self):
        self.plot_reliability_window = ExponReliabilityPlot(self.lambda_value)
        self.plot_reliability_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_reliability_window.show()

    def export_data(self):
        file_name, ext = QFileDialog.getSaveFileName(self, "Экспорт данных", "",
                                                     "Excel (*.xlsx);;")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            if not file_extension:
                file_name += ".xlsx"

            # Генерация диапазона временных значений
            time_upper_limit = stats.expon.ppf(0.99, scale=float(1 / self.lambda_value))  # 99% охвата значений
            time_values = np.linspace(0, time_upper_limit, 1000)

            # Расчет характеристик распределения Вейбулла
            pdf_values = stats.expon.pdf(time_values, scale=float(1 / self.lambda_value))
            cdf_values = stats.expon.cdf(time_values, scale=float(1 / self.lambda_value))
            reliability_values = 1 - cdf_values  # Вероятность безотказной работы

            # Создание словаря данных
            data = {
                'Время': time_values,
                'Функция распределения (CDF)': cdf_values,
                'Плотность распределения (PDF)': pdf_values,
                'Вероятность безотказной работы': reliability_values,
            }

            # Преобразование данных в DataFrame
            df = pd.DataFrame(data)

            # Экспорт данных в Excel
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Expon Data')

                # Получаем объект Workbook для дальнейшего изменения
                workbook = writer.book
                sheet = workbook['Expon Data']

                # Записываем параметры распределения в верхнюю часть таблицы
                sheet['E1'] = 'Параметры нормального распределения:'
                sheet['E2'] = 'Интенсивность отказа (λ):'
                sheet['F2'] = self.lambda_value

                for col in sheet.iter_cols(min_row=1, max_row=1, min_col=1, max_col=5):
                    for cell in col:
                        cell.font = cell.font.copy(bold=True)

                # Применяем автоширину для всех столбцов
                for column_cells in sheet.columns:
                    max_length = 0
                    column_letter = column_cells[0].column_letter
                    for cell in column_cells:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    adjusted_width = max_length + 5
                    sheet.column_dimensions[column_letter].width = adjusted_width

    def set_time(self):
        if self.validate_number(self.time_input):
            self.time = Decimal(self.time_input.text())
        else:
            self.time = None
        self.calculate_with_time()

    def set_reliability_level(self):
        if self.validate_number(self.reliability_level_input):
            self.reliability_level = Decimal(self.reliability_level_input.text())
        else:
            self.reliability_level = None
        self.calculate_time_for_reliability()

    def set_max_failure_probability(self):
        if self.validate_number(self.max_failure_probability_input):
            self.max_failure_probability = Decimal(self.max_failure_probability_input.text())
        else:
            self.max_failure_probability = None
        self.calculate_replacement_time()
