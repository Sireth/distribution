import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, pyqtSignal
from PyQt6.QtGui import QIntValidator, QValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog
)

from windows.weibull.weibull_plot import WeibullDensityPlot, WeibullPlot, WeibullReliabilityPlot, WeibullFailureRatePlot
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


class WeibullWindow(QWidget):

    inputs_validated = pyqtSignal(bool)

    time_changed = pyqtSignal()
    lambda_value_changed = pyqtSignal(object)
    f_t_changed = pyqtSignal(object)
    reliability_changed = pyqtSignal(object)

    time_for_reliability_changed = pyqtSignal(object)

    replacement_time_changed = pyqtSignal(object)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Нормальное распределение")
        self.resize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Параметры
        self.shape_k = 0     # Среднее время до отказа
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

        # Основной макет
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.shape_k_label = QLabel("Параметр формы (b):")
        self.shape_k_input = FocusOutLineEdit()
        self.shape_k_input.setPlaceholderText("Введите параметр формы")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.shape_k_input.setValidator(double_validator)
        layout.addWidget(self.shape_k_label)
        layout.addWidget(self.shape_k_input)
        self.shape_k_input.textChanged.connect(lambda _ : self.validate_number(self.shape_k_input))
        self.shape_k_input.textChanged.connect(lambda _: self.validate_inputs())


        self.scale_lambda_label = QLabel("Параметр масштаба (a):")
        self.scale_lambda_input = FocusOutLineEdit()
        self.scale_lambda_input.setPlaceholderText("Введите параметр масштаба")
        regex = QRegularExpression(r"^(?!0$)(?!0\.0+$)\d+(\.\d+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.scale_lambda_input.setValidator(double_validator)
        layout.addWidget(self.scale_lambda_label)
        layout.addWidget(self.scale_lambda_input)
        self.scale_lambda_input.textChanged.connect(lambda _ : self.validate_number(self.scale_lambda_input))
        self.scale_lambda_input.textChanged.connect(lambda _: self.validate_inputs())

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


        self.plot_failure_rate_btn = QPushButton("Построить график интенсивности отказов")
        layout.addWidget(self.plot_failure_rate_btn)
        self.plot_failure_rate_btn.clicked.connect(self.plot_failure_rate)
        self.inputs_validated.connect(self.plot_failure_rate_btn.setEnabled)
        self.plot_failure_rate_btn.setEnabled(False)


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

        self.lambda_label = QLabel("Интенсивность отказа (λ(t)):")
        self.lambda_input = QLineEdit()
        self.lambda_input.setReadOnly(True)
        layout.addWidget(self.lambda_label)
        layout.addWidget(self.lambda_input)
        self.lambda_value_changed.connect(lambda value: self.lambda_input.setText(str(value))
                                                 if value is not None
                                                 else self.lambda_input.setText(""))

        self.f_label = QLabel("Вероятность отказа при времени t (F(t)):")
        self.f_input = QLineEdit()
        self.f_input.setReadOnly(True)
        layout.addWidget(self.f_label)
        layout.addWidget(self.f_input)
        self.f_t_changed.connect(lambda value: self.f_input.setText(str(value))
                                        if value is not None
                                        else self.f_input.setText(""))

        self.reliability_label = QLabel("Вероятность безотказной работы до времени t (R(t)):")
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

            k_values = np.arange(0, self.n + 1)
            pmf_values = stats.poisson.pmf(k_values, float(self.lambda_value))

            data = {
                'k': k_values,
                'Вероятность': pmf_values
            }

            df = pd.DataFrame(data)
            # Создаем объект ExcelWriter
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                # Записываем данные в лист 'Poisson Data'
                df.to_excel(writer, index=False, sheet_name='Poisson Data')

                # Получаем объект Workbook для дальнейшего изменения
                workbook = writer.book
                sheet = workbook['Poisson Data']

                sheet['C1'] = 'Размер выборки (n)'
                sheet['C2'] = self.n
                sheet['D1'] = 'Интенсивность отказов (λ)'
                sheet['D2'] = self.lambda_value
                sheet['E1'] = 'Вероятность успеха (p)'
                sheet['E2'] = self.p
                sheet['F1'] = 'Вероятность неудачи (q)'
                sheet['F2'] = self.q

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
