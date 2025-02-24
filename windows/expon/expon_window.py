import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
)

from windows.base_button import BaseButton
from windows.base_label import BaseLabel
from windows.base_line_edit import BaseLineEdit, FocusOutLineEdit
from windows.base_substrate import BaseSubstrate
from windows.base_window import BaseWindow
from windows.expon.expon_plot import ExponDensityPlot, ExponPlot, ExponReliabilityPlot
import scipy.stats as stats

from decimal import Decimal

class ExponWindow(BaseWindow):

    inputs_validated = pyqtSignal(bool)

    time_changed = pyqtSignal()
    f_t_changed = pyqtSignal(object)
    reliability_changed = pyqtSignal(object)
    failure_changed = pyqtSignal(object)

    time_for_reliability_changed = pyqtSignal(object)

    replacement_time_changed = pyqtSignal(object)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.plot_density_window = None
        self.plot_window = None
        self.plot_reliability_window = None
        self.setWindowTitle("Экспоненциальное распределение")

        # Параметры
        self.lambda_value = None  # Интенсивность отказа
        self.Mtbf         = None  # Средняя наработка на отказ

        self.time = None
        self.f_t = None           # Вероятность отказа
        self.reliability = None   # Вероятность безотказной работы
        self.failure = None       # Вероятность отказа

        self.reliability_level = None
        self.time_for_reliability = None

        self.max_failure_probability = None
        self.replacement_time = None

        self.check = False


        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        self.lambda_value_label = BaseLabel("Интенсивность отказов (λ):", sub)
        self.lambda_value_input = FocusOutLineEdit(sub)
        self.lambda_value_input.setPlaceholderText("Введите интенсивность отказов")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.lambda_value_input.setValidator(double_validator)
        sub.layout().addWidget(self.lambda_value_label)
        sub.layout().addWidget(self.lambda_value_input)
        self.lambda_value_input.textChanged.connect(lambda _ : self.validate_number(self.lambda_value_input))
        self.lambda_value_input.textChanged.connect(lambda _: self.calculate_Mtbf() if self.lambda_value_input.hasFocus() else None)
        self.lambda_value_input.focusLost.connect(self.calculate_lambda_value)
        self.lambda_value_input.textChanged.connect(lambda _: self.validate_inputs())

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        self.Mtbf_label = BaseLabel("Средняя наработка на отказ (T):", sub)
        self.Mtbf_input = FocusOutLineEdit(sub)
        self.Mtbf_input.setPlaceholderText("Введите среднюю наработку на отказ")
        regex = QRegularExpression(r"^\d*(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.Mtbf_input.setValidator(double_validator)
        sub.layout().addWidget(self.Mtbf_label)
        sub.layout().addWidget(self.Mtbf_input)
        self.Mtbf_input.textChanged.connect(lambda _: self.validate_number(self.Mtbf_input))
        self.Mtbf_input.textChanged.connect(lambda _: self.calculate_lambda_value() if self.Mtbf_input.hasFocus() else None)
        self.Mtbf_input.focusLost.connect(self.calculate_Mtbf)
        self.Mtbf_input.textChanged.connect(lambda _: self.validate_inputs())

        self.plot_distribution_density_btn = BaseButton("Построить график плотности распределения")
        self.layout().addWidget(self.plot_distribution_density_btn)
        self.plot_distribution_density_btn.clicked.connect(self.plot_distribution_density)
        self.inputs_validated.connect(self.plot_distribution_density_btn.setEnabled)
        self.plot_distribution_density_btn.setEnabled(False)


        self.plot_distribution_btn = BaseButton("Построить график распределения")
        self.layout().addWidget(self.plot_distribution_btn)
        self.plot_distribution_btn.clicked.connect(self.plot_distribution)
        self.inputs_validated.connect(self.plot_distribution_btn.setEnabled)
        self.plot_distribution_btn.setEnabled(False)


        self.plot_reliability_btn = BaseButton("Построить график вероятности безотказной работы")
        self.layout().addWidget(self.plot_reliability_btn)
        self.plot_reliability_btn.clicked.connect(self.plot_reliability)
        self.inputs_validated.connect(self.plot_reliability_btn.setEnabled)
        self.plot_reliability_btn.setEnabled(False)

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())
        tmp2 = QWidget(tmp)
        tmp.layout().addWidget(tmp2)
        tmp2.setLayout(QHBoxLayout())

        self.time_label = BaseLabel("Наработка на отказ (t):", tmp2)
        self.time_input = FocusOutLineEdit(tmp2)
        self.time_input.setPlaceholderText("Введите наработку на отказ")
        regex = QRegularExpression(r"^\d*(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.time_input.setValidator(double_validator)
        tmp2.layout().addWidget(self.time_label)
        tmp2.layout().addWidget(self.time_input)
        self.time_input.textChanged.connect(lambda _ : self.set_time())

        self.inputs_validated.connect(lambda _: self.calculate_with_time())
        tmp.layout().addWidget(tmp2)


        self.f_label = BaseLabel("Вероятность безотказной работы до наработки t (P(t)):", tmp)
        self.f_input = BaseLineEdit(tmp)
        self.f_input.setReadOnly(True)
        tmp.layout().addWidget(self.f_label)
        tmp.layout().addWidget(self.f_input)
        self.f_t_changed.connect(lambda value: self.f_input.setText(str(value))
                                        if value is not None
                                        else self.f_input.setText(""))

        self.reliability_label = BaseLabel("Вероятность безотказной работы (P(t)):", tmp)
        self.reliability_input = BaseLineEdit(tmp)
        self.reliability_input.setReadOnly(True)
        tmp.layout().addWidget(self.reliability_label)
        tmp.layout().addWidget(self.reliability_input)
        self.reliability_changed.connect(lambda value: self.reliability_input.setText(str(value))
                                                if value is not None
                                                else self.reliability_input.setText(""))

        self.failure_label = BaseLabel("Вероятность отказа (1 - P(t)):", tmp)
        self.failure_input = BaseLineEdit(tmp)
        self.failure_input.setReadOnly(True)
        tmp.layout().addWidget(self.failure_label)
        tmp.layout().addWidget(self.failure_input)
        self.failure_changed.connect(lambda value: self.failure_input.setText(str(value))
                                                if value is not None
                                                else self.failure_input.setText(""))

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        tmp.setLayout(QVBoxLayout())
        sub.layout().addWidget(tmp)

        self.reliability_level_label_title = BaseLabel("Определение времени наработки на отказ", tmp)
        tmp2 = QWidget(tmp)
        tmp2.setLayout(QHBoxLayout())
        self.reliability_level_label = BaseLabel("Надежность:", tmp2)
        self.reliability_level_input = FocusOutLineEdit(tmp2)
        self.reliability_level_input.setPlaceholderText("Введите надежность")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.reliability_level_input.setValidator(double_validator)
        tmp.layout().addWidget(self.reliability_level_label_title)
        tmp2.layout().addWidget(self.reliability_level_label)
        tmp2.layout().addWidget(self.reliability_level_input)
        self.reliability_level_input.textChanged.connect(lambda _ : self.set_reliability_level())
        tmp.layout().addWidget(tmp2)

        self.time_for_reliability_label = BaseLabel("Время наработки на отказ:", tmp)
        self.time_for_reliability_input = BaseLineEdit(tmp)
        self.time_for_reliability_input.setReadOnly(True)
        tmp.layout().addWidget(self.time_for_reliability_label)
        tmp.layout().addWidget(self.time_for_reliability_input)
        self.time_for_reliability_changed.connect(lambda value: self.time_for_reliability_input.setText(str(value))
                                                if value is not None
                                                else self.time_for_reliability_input.setText(""))

        self.inputs_validated.connect(lambda _: self.calculate_time_for_reliability())

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        tmp.setLayout(QVBoxLayout())
        sub.layout().addWidget(tmp)

        self.max_failure_probability_label_title = BaseLabel("Рассчитать минимальную наработку до замены", tmp)
        tmp2 = QWidget(tmp)
        tmp2.setLayout(QHBoxLayout())
        self.max_failure_probability_label = BaseLabel("Вероятность отказа:", tmp2)
        self.max_failure_probability_input = FocusOutLineEdit(tmp2)
        self.max_failure_probability_input.setPlaceholderText("Введите вероятность отказа")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.max_failure_probability_input.setValidator(double_validator)
        tmp.layout().addWidget(self.max_failure_probability_label_title)
        tmp2.layout().addWidget(self.max_failure_probability_label)
        tmp2.layout().addWidget(self.max_failure_probability_input)
        self.max_failure_probability_input.textChanged.connect(lambda _ : self.set_max_failure_probability())
        tmp.layout().addWidget(tmp2)

        self.replacement_time_label = BaseLabel("Минимальная наработка до замены:", tmp)
        self.replacement_time_input = BaseLineEdit(tmp)
        self.replacement_time_input.setReadOnly(True)
        tmp.layout().addWidget(self.replacement_time_label)
        tmp.layout().addWidget(self.replacement_time_input)
        self.replacement_time_changed.connect(lambda value: self.replacement_time_input.setText(str(value))
                                                if value is not None
                                                else self.replacement_time_input.setText(""))

        self.inputs_validated.connect(lambda _: self.calculate_replacement_time())

        self.export_btn = BaseButton("Экспортировать данные")
        self.layout().addWidget(self.export_btn)
        self.export_btn.clicked.connect(self.export_data)
        self.inputs_validated.connect(self.export_btn.setEnabled)
        self.export_btn.setEnabled(False)




    def calculate_with_time(self):
        if (self.time is None) or (not self.check):
            self.f_t = None
            self.reliability = None
            self.failure = None
        else:
            self.f_t = stats.expon.pdf(float(self.time), scale=float(1 / self.lambda_value))
            self.reliability = 1 - stats.expon.cdf(float(self.time), scale=float(1 / self.lambda_value))
            self.failure = stats.expon.cdf(float(self.time), scale=float(1 / self.lambda_value))

        self.f_t_changed.emit(self.f_t)
        self.reliability_changed.emit(self.reliability)
        self.failure_changed.emit(self.failure)

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

    def calculate_Mtbf(self):
        if not (self.validate_number(self.lambda_value_input)):
            return
        self.Mtbf = Decimal(1) / Decimal(self.lambda_value_input.text())
        self.Mtbf_input.setText(str(self.Mtbf))
        return self.Mtbf

    def calculate_lambda_value(self):
        if not (self.validate_number(self.Mtbf_input)):
            return
        self.lambda_value = Decimal(1) / Decimal(self.Mtbf_input.text())
        self.lambda_value_input.setText(str(self.lambda_value))
        return self.lambda_value
