import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, pyqtSignal
from PyQt6.QtGui import QIntValidator, QValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog
)

from windows.poisson.poisson_plot import PlotWindow
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


class PoissonWindow(QWidget):

    inputs_validated = pyqtSignal(bool)
    n_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Распределение Пуассона")
        self.resize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Параметры
        self.n = 0  # Количество испытаний
        self.p = 0  # Вероятность успеха
        self.q = 0  # Вероятность неудачи
        self.k = 0  # Количество событий

        self.lambda_value = 0
        self.probability = 0

        self.check = False

        # Основной макет
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.n_label = QLabel("Количество испытаний (n):")
        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("Введите количество испытаний")
        self.n_input.setValidator(QIntValidator(1, 9999999))
        layout.addWidget(self.n_label)
        layout.addWidget(self.n_input)
        self.n_input.textChanged.connect(lambda _ : self.validate_number(self.n_input))
        self.n_input.textChanged.connect(lambda _ : self.validate_inputs())

        self.p_label = QLabel("Вероятность успеха (p):")
        self.p_input = FocusOutLineEdit()
        self.p_input.setPlaceholderText("Введите вероятность успеха")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.p_input.setValidator(double_validator)
        layout.addWidget(self.p_label)
        layout.addWidget(self.p_input)
        self.p_input.textChanged.connect(lambda _ : self.validate_number(self.p_input))
        self.p_input.textChanged.connect(lambda _ : self.calculate_q() if self.p_input.hasFocus() else None)
        self.p_input.focusLost.connect(self.calculate_p)
        self.p_input.textChanged.connect(lambda _: self.validate_inputs())


        self.q_label = QLabel("Вероятность неудачи (q):")
        self.q_input = FocusOutLineEdit()
        self.q_input.setPlaceholderText("Введите вероятность неудачи")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.q_input.setValidator(double_validator)
        layout.addWidget(self.q_label)
        layout.addWidget(self.q_input)
        self.q_input.textChanged.connect(lambda _ : self.validate_number(self.q_input))
        self.q_input.textChanged.connect(lambda _ : self.calculate_p() if self.q_input.hasFocus() else None)
        self.q_input.focusLost.connect(self.calculate_q)
        self.q_input.textChanged.connect(lambda _: self.validate_inputs())

        self.lambda_label = QLabel("Интенсивность отказов (λ):")
        self.lambda_input = QLineEdit()
        self.lambda_input.setReadOnly(True)
        layout.addWidget(self.lambda_label)
        layout.addWidget(self.lambda_input)
        self.inputs_validated.connect(lambda _ : self.lambda_input.setText(str(self.lambda_value)))


        self.plot_distribution_btn = QPushButton("Построить график плотности распределения")
        layout.addWidget(self.plot_distribution_btn)
        self.plot_distribution_btn.clicked.connect(self.plot_distribution)
        self.inputs_validated.connect(self.plot_distribution_btn.setEnabled)
        self.plot_distribution_btn.setEnabled(False)

        self.k_label = QLabel("Количество событий (k):")
        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("Введите количество событий")
        self.k_input.setValidator(QIntValidator(0, 9999999))
        layout.addWidget(self.k_label)
        layout.addWidget(self.k_input)
        self.k_input.textChanged.connect(lambda _ : self.validate_number(self.k_input))
        self.k_input.textChanged.connect(lambda _ : self.calculate_probability())
        self.n_input.textChanged.connect(lambda _ : self.change_k_validator())

        self.probability_label = QLabel("Вероятность безотказной работы (P(k)):")
        self.probability_input = QLineEdit()
        self.probability_input.setReadOnly(True)
        layout.addWidget(self.probability_label)
        layout.addWidget(self.probability_input)
        self.n_changed.connect(lambda _ : self.calculate_probability())


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

    def change_k_validator(self):
        top = self.n
        if not self.validate_number(self.n_input):
            top = 0
        else :
            top = int(self.n_input.text())

        self.k_input.validator().setTop(top)

    def calculate_probability(self):
        if not (self.validate_number(self.k_input) and self.check):
            self.probability_input.setText("")
            self.probability = 0
            return

        self.k = int(self.k_input.text())
        self.probability = stats.poisson.pmf(self.k, float(self.lambda_value))
        self.probability_input.setText(str(self.probability))
        return self.probability

    def calculate_p(self):
        if not (self.validate_number(self.q_input)):
            return
        self.p = Decimal(1) - Decimal(self.q_input.text())
        self.p_input.setText(str(self.p))
        return self.p

    def calculate_q(self):
        if not (self.validate_number(self.p_input)):
            return
        self.q = Decimal(1) - Decimal(self.p_input.text())
        self.q_input.setText(str(self.q))
        return self.q


    def validate_inputs(self):
        self.check = True
        if not self.validate_number(self.n_input):
            self.check = False
        if not self.validate_number(self.p_input):
            self.check = False
        if not self.validate_number(self.q_input):
            self.check = False

        if self.check:
            self.set_values()

        self.inputs_validated.emit(self.check)

        return self.check

    def set_values(self):

        self.n = int(self.n_input.text())
        self.n_changed.emit(self.n)
        self.p = Decimal(self.p_input.text())
        self.q = Decimal(1) - Decimal(self.p)

        self.lambda_value = Decimal(self.n) * Decimal(self.p)
        self.lambda_input.setText(str(Decimal(self.lambda_value)))


    def calculate_lambda(self):
        self.n = int(self.n_input.text())
        self.p = Decimal(self.p_input.text())


        # Вычисление значения λ
        self.lambda_value = self.n * self.p
        self.lambda_input.setText(str(self.lambda_value))

    def plot_distribution(self):
        self.plot_window = PlotWindow(self.lambda_value, self.n)
        self.plot_window.show()

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