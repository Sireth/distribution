import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
)

from windows.base_button import BaseButton
from windows.base_label import BaseLabel
from windows.base_line_edit import BaseLineEdit, FocusOutLineEdit
from windows.base_substrate import BaseSubstrate
from windows.base_window import BaseWindow
from windows.poisson.poisson_plot import PoissonDensityPlot, PoissonPlot
import scipy.stats as stats

from decimal import Decimal


class PoissonWindow(BaseWindow):

    inputs_validated = pyqtSignal(bool)
    n_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Распределение Пуассона")

        # Параметры
        self.n = 0  # Количество испытаний
        self.p = 0  # Вероятность успеха
        self.q = 0  # Вероятность неудачи
        self.k = 0  # Количество событий

        self.lambda_value = 0
        self.probability_eq = 0
        self.probability_eq_less = 0
        self.k_value = 0 # Наиболее вероятное число отказов

        self.check = False

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)

        self.n_label = BaseLabel("Количество испытаний (n):", sub)
        self.n_input = BaseLineEdit(sub)
        self.n_input.setPlaceholderText("Введите количество испытаний")
        self.n_input.setValidator(QIntValidator(1, 9999999))
        sub.layout().addWidget(self.n_label)
        sub.layout().addWidget(self.n_input)
        self.n_input.textChanged.connect(lambda _ : self.validate_number(self.n_input))
        self.n_input.textChanged.connect(lambda _ : self.validate_inputs())


        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)

        self.p_label = BaseLabel("Вероятность безотказной работы (p):", sub)
        self.p_input = FocusOutLineEdit(sub)
        self.p_input.setPlaceholderText("Введите вероятность безотказной работы")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.p_input.setValidator(double_validator)
        sub.layout().addWidget(self.p_label)
        sub.layout().addWidget(self.p_input)
        self.p_input.textChanged.connect(lambda _ : self.validate_number(self.p_input))
        self.p_input.textChanged.connect(lambda _ : self.calculate_q() if self.p_input.hasFocus() else None)
        self.p_input.focusLost.connect(self.calculate_p)
        self.p_input.textChanged.connect(lambda _: self.validate_inputs())


        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)

        self.q_label = BaseLabel("Вероятность отказа (q):", sub)
        self.q_input = FocusOutLineEdit(sub)
        self.q_input.setPlaceholderText("Введите вероятность отказа")
        regex = QRegularExpression(r"^0(\.\d+)?|1(\.0+)?$")
        double_validator = QRegularExpressionValidator(regex)
        self.q_input.setValidator(double_validator)
        sub.layout().addWidget(self.q_label)
        sub.layout().addWidget(self.q_input)
        self.q_input.textChanged.connect(lambda _ : self.validate_number(self.q_input))
        self.q_input.textChanged.connect(lambda _ : self.calculate_p() if self.q_input.hasFocus() else None)
        self.q_input.focusLost.connect(self.calculate_q)
        self.q_input.textChanged.connect(lambda _: self.validate_inputs())


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

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())

        self.lambda_label = BaseLabel("Интенсивность отказов (λ):", tmp)
        self.lambda_label.setToolTip("Параметр распределения Пуассона")
        self.lambda_input = BaseLineEdit(tmp)
        self.lambda_input.setReadOnly(True)
        tmp.layout().addWidget(self.lambda_label)
        tmp.layout().addWidget(self.lambda_input)
        self.inputs_validated.connect(lambda _: self.lambda_input.setText(str(self.lambda_value)))

        self.k_value_label = BaseLabel("Наиболее вероятное число отказов (k):", tmp)
        self.k_value_input = BaseLineEdit(tmp)
        self.k_value_input.setReadOnly(True)
        self.inputs_validated.connect(self.calculate_k)
        tmp.layout().addWidget(self.k_value_label)
        tmp.layout().addWidget(self.k_value_input)

        sub = BaseSubstrate(self)
        self.layout().addWidget(sub)
        tmp = QWidget(sub)
        sub.layout().addWidget(tmp)
        tmp.setLayout(QVBoxLayout())
        tmp2 = QWidget(tmp)
        tmp.layout().addWidget(tmp2)
        tmp2.setLayout(QHBoxLayout())

        self.m_label = BaseLabel("Количество событий m в n испытаниях (m):", tmp2)
        self.m_input = BaseLineEdit(tmp2)
        self.m_input.setPlaceholderText("Введите количество событий m в n испытаниях")
        self.m_input.setValidator(QIntValidator(0, 9999999))
        tmp2.layout().addWidget(self.m_label)
        tmp2.layout().addWidget(self.m_input)
        self.m_input.textChanged.connect(lambda _ : self.validate_number(self.m_input))
        self.m_input.textChanged.connect(lambda _ : self.calculate_probability_eq())
        self.m_input.textChanged.connect(lambda _ : self.calculate_probability_eq_less())
        self.n_input.textChanged.connect(lambda _ : self.change_m_validator())
        self.inputs_validated.connect(lambda _: self.calculate_probability_eq())
        self.inputs_validated.connect(lambda _: self.calculate_probability_eq_less())

        self.probability_eq_label = BaseLabel("Вероятность появления события m в n испытаниях (P(X = m)):", tmp)
        self.probability_eq_input = BaseLineEdit(tmp)
        self.probability_eq_input.setReadOnly(True)
        tmp.layout().addWidget(self.probability_eq_label)
        tmp.layout().addWidget(self.probability_eq_input)
        self.n_changed.connect(lambda _ : self.calculate_probability_eq())

        self.probability_eq_less_label = BaseLabel("Вероятность появления события m в n испытаниях (P(X ≤ m)):", tmp)
        self.probability_eq_less_input = BaseLineEdit(tmp)
        self.probability_eq_less_input.setReadOnly(True)
        tmp.layout().addWidget(self.probability_eq_less_label)
        tmp.layout().addWidget(self.probability_eq_less_input)
        self.n_changed.connect(lambda _ : self.calculate_probability_eq_less())


        self.export_btn = BaseButton("Экспортировать данные")
        self.layout().addWidget(self.export_btn)
        self.export_btn.clicked.connect(self.export_data)
        self.inputs_validated.connect(self.export_btn.setEnabled)
        self.export_btn.setEnabled(False)

    def change_m_validator(self):
        top = self.n
        if not self.validate_number(self.n_input):
            top = 0
        else:
            top = int(self.n_input.text())

        self.m_input.validator().setTop(top)
        self.validate_number(self.m_input)

    def calculate_probability_eq(self):
        self.change_m_validator()
        if not (self.validate_number(self.m_input) and self.check):
            self.probability_eq_input.setText("")
            self.probability_eq = 0
            return

        self.k = int(self.m_input.text())
        self.probability_eq = stats.poisson.pmf(self.k, float(self.lambda_value))
        self.probability_eq_input.setText(str(self.probability_eq))
        return self.probability_eq

    def calculate_probability_eq_less(self):
        self.change_m_validator()
        if not (self.validate_number(self.m_input) and self.check):
            self.probability_eq_less_input.setText("")
            self.probability_eq_less = 0
            return

        self.k = int(self.m_input.text())
        self.probability_eq_less = stats.poisson.cdf(self.k, float(self.lambda_value))
        self.probability_eq_less_input.setText(str(self.probability_eq_less))
        return self.probability_eq_less

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

    def calculate_k(self):
        self.k_value = 0
        if self.check:
            k_values = np.arange(0, self.n + 1)
            pmf_values = stats.poisson.cdf(k_values, float(self.lambda_value))
            self.k_value = np.argmax(pmf_values)
        self.k_value_input.setText(str(self.k_value))


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

    def plot_distribution_density(self):
        self.plot_density_window = PoissonDensityPlot(self.lambda_value, self.n)
        self.plot_density_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.plot_density_window.show()

    def plot_distribution(self):
        self.plot_window = PoissonPlot(self.lambda_value, self.n)
        self.plot_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
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
            cdf_values = stats.poisson.cdf(k_values, float(self.lambda_value))

            data = {
                'm': k_values,
                'Функция распределения (CDF)': cdf_values,
                'Плотность распределения (PMF)': pmf_values,
            }

            df = pd.DataFrame(data)
            # Создаем объект ExcelWriter
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                # Записываем данные в лист 'Poisson Data'
                df.to_excel(writer, index=False, sheet_name='Poisson Data')

                # Получаем объект Workbook для дальнейшего изменения
                workbook = writer.book
                sheet = workbook['Poisson Data']

                sheet['D1'] = 'Размер выборки (n)'
                sheet['D2'] = self.n
                sheet['E1'] = 'Интенсивность отказов (λ)'
                sheet['E2'] = self.lambda_value
                sheet['F1'] = 'Вероятность безотказной работы (p)'
                sheet['F2'] = self.p
                sheet['G1'] = 'Вероятность отказа (q)'
                sheet['G2'] = self.q


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