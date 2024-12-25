import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, pyqtSignal
from PyQt6.QtGui import QIntValidator, QValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QFileDialog, QWidget, QVBoxLayout, QHBoxLayout
)

from windows.base_button import BaseButton
from windows.base_label import BaseLabel
from windows.base_line_edit import FocusOutLineEdit, BaseLineEdit
from windows.base_substrate import BaseSubstrate
from windows.base_window import BaseWindow
from windows.weibull.weibull_plot import WeibullDensityPlot, WeibullPlot, WeibullReliabilityPlot, WeibullFailureRatePlot
import scipy.stats as stats

from decimal import Decimal


class WeibullWindow(BaseWindow):

    inputs_validated = pyqtSignal(bool)

    time_changed = pyqtSignal()
    lambda_value_changed = pyqtSignal(object)
    f_t_changed = pyqtSignal(object)
    reliability_changed = pyqtSignal(object)

    time_for_reliability_changed = pyqtSignal(object)

    replacement_time_changed = pyqtSignal(object)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Распределение Вейбулла")

        # Параметры
        self.shape_k = 0       # Среднее время до отказа
        self.scale_lambda = 0  # Стандартное отклонение

        self.time = None
        self.lambda_value = None  # Интенсивность отказа
        self.f_t = None           # Вероятность отказа
        self.reliability = None   # Вероятность безотказной работы

        self.reliability_level = None
        self.time_for_reliability = None

        self.max_failure_probability = None
        self.replacement_time = None

        self.check = False

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)

        self.shape_k_label = BaseLabel("Параметр формы (b):", sub)
        self.shape_k_input = FocusOutLineEdit(sub)
        self.shape_k_input.setPlaceholderText("Введите параметр формы")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.shape_k_input.setValidator(double_validator)
        sub.layout().addWidget(self.shape_k_label)
        sub.layout().addWidget(self.shape_k_input)
        self.shape_k_input.textChanged.connect(lambda _ : self.validate_number(self.shape_k_input))
        self.shape_k_input.textChanged.connect(lambda _: self.validate_inputs())

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)

        self.scale_lambda_label = BaseLabel("Параметр масштаба (a):", sub)
        self.scale_lambda_input = FocusOutLineEdit(sub)
        self.scale_lambda_input.setPlaceholderText("Введите параметр масштаба")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.scale_lambda_input.setValidator(double_validator)
        sub.layout().addWidget(self.scale_lambda_label)
        sub.layout().addWidget(self.scale_lambda_input)
        self.scale_lambda_input.textChanged.connect(lambda _ : self.validate_number(self.scale_lambda_input))
        self.scale_lambda_input.textChanged.connect(lambda _: self.validate_inputs())

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


        self.plot_failure_rate_btn = BaseButton("Построить график интенсивности отказов")
        self.layout().addWidget(self.plot_failure_rate_btn)
        self.plot_failure_rate_btn.clicked.connect(self.plot_failure_rate)
        self.inputs_validated.connect(self.plot_failure_rate_btn.setEnabled)
        self.plot_failure_rate_btn.setEnabled(False)

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())
        tmp2 = QWidget(tmp)
        tmp.layout().addWidget(tmp2)
        tmp2.setLayout(QHBoxLayout())

        self.time_label = BaseLabel("Время (t):", tmp2)
        self.time_input = FocusOutLineEdit(tmp2)
        self.time_input.setPlaceholderText("Введите время")
        regex = QRegularExpression(r"^\d*(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.time_input.setValidator(double_validator)
        tmp2.layout().addWidget(self.time_label)
        tmp2.layout().addWidget(self.time_input)
        self.time_input.textChanged.connect(lambda _ : self.set_time())
        tmp.layout().addWidget(tmp2)

        self.inputs_validated.connect(lambda _: self.calculate_with_time())

        self.lambda_label = BaseLabel("Интенсивность отказа (λ(t)):", tmp)
        self.lambda_input = BaseLineEdit(tmp)
        self.lambda_input.setReadOnly(True)
        tmp.layout().addWidget(self.lambda_label)
        tmp.layout().addWidget(self.lambda_input)
        self.lambda_value_changed.connect(lambda value: self.lambda_input.setText(str(value))
                                                 if value is not None
                                                 else self.lambda_input.setText(""))

        self.f_label = BaseLabel("Вероятность отказа при времени t (F(t)):", tmp)
        self.f_input = BaseLineEdit(tmp)
        self.f_input.setReadOnly(True)
        tmp.layout().addWidget(self.f_label)
        tmp.layout().addWidget(self.f_input)
        self.f_t_changed.connect(lambda value: self.f_input.setText(str(value))
                                        if value is not None
                                        else self.f_input.setText(""))

        self.reliability_label = BaseLabel("Вероятность безотказной работы до времени t (R(t)):", tmp)
        self.reliability_input = BaseLineEdit(tmp)
        self.reliability_input.setReadOnly(True)
        tmp.layout().addWidget(self.reliability_label)
        tmp.layout().addWidget(self.reliability_input)
        self.reliability_changed.connect(lambda value: self.reliability_input.setText(str(value))
                                                if value is not None
                                                else self.reliability_input.setText(""))

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())
        tmp2 = QWidget(tmp)
        tmp.layout().addWidget(tmp2)
        tmp2.setLayout(QHBoxLayout())

        self.reliability_level_label_title = BaseLabel("Определение времени наработки на отказ", tmp)
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
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())
        tmp2 = QWidget(tmp)
        tmp.layout().addWidget(tmp2)
        tmp2.setLayout(QHBoxLayout())

        self.max_failure_probability_label_title = BaseLabel("Рассчитать минимальное время до замены", tmp)
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

        self.replacement_time_label = BaseLabel("Минимальное время замены:", tmp)
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
            self.lambda_value = None
            self.f_t = None
            self.reliability = None
        else:
            self.f_t = stats.weibull_min.pdf(float(self.time), c=float(self.shape_k), scale=float(self.scale_lambda))
            self.reliability = 1 - stats.weibull_min.cdf(float(self.time), c=float(self.shape_k), scale=float(self.scale_lambda))
            self.lambda_value = self.f_t / self.reliability

        self.lambda_value_changed.emit(self.lambda_value)
        self.f_t_changed.emit(self.f_t)
        self.reliability_changed.emit(self.reliability)

    def calculate_time_for_reliability(self):
        if (self.reliability_level is None) or (not self.check):
            self.time_for_reliability = None
        else:
            self.time_for_reliability = stats.weibull_min.ppf(float(1 - self.reliability_level), c=float(self.shape_k), scale=float(self.scale_lambda))

        self.time_for_reliability_changed.emit(self.time_for_reliability)

    def calculate_replacement_time(self):
        if (self.max_failure_probability is None) or (not self.check):
            self.replacement_time = None
        else:
            self.replacement_time = stats.weibull_min.ppf(float(self.max_failure_probability), c=float(self.shape_k), scale=float(self.scale_lambda))

        self.replacement_time_changed.emit(self.replacement_time)


    def validate_inputs(self):
        self.check = True
        if not self.validate_number(self.shape_k_input):
            self.check = False
        if not self.validate_number(self.scale_lambda_input):
            self.check = False

        if self.check:
            self.set_values()

        self.inputs_validated.emit(self.check)

        return self.check

    def set_values(self):

        self.shape_k = Decimal(self.shape_k_input.text())
        self.scale_lambda = Decimal(self.scale_lambda_input.text())

    def plot_distribution_density(self):
        self.plot_density_window = WeibullDensityPlot(self.shape_k, self.scale_lambda)
        self.plot_density_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_density_window.show()

    def plot_distribution(self):
        self.plot_window = WeibullPlot(self.shape_k, self.scale_lambda)
        self.plot_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_window.show()

    def plot_reliability(self):
        self.plot_reliability_window = WeibullReliabilityPlot(self.shape_k, self.scale_lambda)
        self.plot_reliability_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_reliability_window.show()

    def plot_failure_rate(self):
        self.plot_failure_rate_window = WeibullFailureRatePlot(self.shape_k, self.scale_lambda)
        self.plot_failure_rate_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_failure_rate_window.show()

    def export_data(self):
        file_name, ext = QFileDialog.getSaveFileName(self, "Экспорт данных", "",
                                                     "Excel (*.xlsx);;")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            if not file_extension:
                file_name += ".xlsx"

            # Генерация диапазона временных значений
            time_upper_limit = stats.weibull_min.ppf(0.99, c=float(self.shape_k), scale=float(self.scale_lambda))  # 99% охвата значений
            time_values = np.linspace(0, time_upper_limit, 1000)

            # Расчет характеристик распределения Вейбулла
            pdf_values = stats.weibull_min.pdf(time_values, c=float(self.shape_k), scale=float(self.scale_lambda))
            cdf_values = stats.weibull_min.cdf(time_values, c=float(self.shape_k), scale=float(self.scale_lambda))
            reliability_values = 1 - cdf_values  # Вероятность безотказной работы
            failure_rate_values = pdf_values / reliability_values  # Интенсивность отказов

            # Создание словаря данных
            data = {
                'Время': time_values,
                'Функция распределения (CDF)': cdf_values,
                'Плотность распределения (PDF)': pdf_values,
                'Вероятность безотказной работы': reliability_values,
                'Интенсивность отказов': failure_rate_values
            }

            # Преобразование данных в DataFrame
            df = pd.DataFrame(data)

            # Экспорт данных в Excel
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Weibull Data')

                # Получаем объект Workbook для дальнейшего изменения
                workbook = writer.book
                sheet = workbook['Weibull Data']

                # Записываем параметры распределения в верхнюю часть таблицы

                sheet['F1'] = 'Параметры распределения Вейбулла:'
                sheet['F2'] = 'Параметр формы (k)'
                sheet['G2'] = self.shape_k
                sheet['F3'] = 'Параметр масштаба (λ)'
                sheet['G3'] = self.scale_lambda

                for col in sheet.iter_cols(min_row=1, max_row=1, min_col=1, max_col=7):
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
