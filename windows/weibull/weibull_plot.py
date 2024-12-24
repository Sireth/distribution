import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PyQt6.QtGui import QPainter, QImage
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
import scipy.stats as stats

class WeibullDensityPlot(QWidget):
    def __init__(self, shape_k, scale_lambda):
        super().__init__()

        self.shape_k = shape_k
        self.scale_lambda = scale_lambda

        self.setWindowTitle("График плотности распределения Вейбулла")
        self.setGeometry(100, 100, 800, 600)

        # Создаем фигуру для графика
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Добавляем холст в макет
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Кнопки для сохранения и копирования графика
        self.save_button = QPushButton("Сохранить график")
        self.copy_button = QPushButton("Копировать график")
        self.save_button.clicked.connect(self.save_plot)
        self.copy_button.clicked.connect(self.copy_plot)

        layout.addWidget(self.save_button)
        layout.addWidget(self.copy_button)

        time_upper_limit = stats.weibull_min.ppf(0.99, c=float(shape_k), scale=float(self.scale_lambda))  # 99% охвата значений
        self.time = np.linspace(0, time_upper_limit, 1000)

        self.pdf_values = stats.weibull_min.pdf(self.time, c=float(shape_k), scale=float(self.scale_lambda))

        ax.plot(self.time, self.pdf_values, label="Плотность вероятности (PDF)", color="blue")

        ax.set_title("Плотность вероятности (PDF)")
        ax.set_xlabel("Время до отказа")
        ax.set_ylabel("Плотность вероятности")
        ax.grid()
        ax.legend()

        # Обновляем холст, чтобы отобразить график
        self.canvas.draw()

    def save_plot(self):
        """Сохранение графика в файл."""
        file_name, ext = QFileDialog.getSaveFileName(self, "Сохранить график", "",
                                                "PNG файлы (*.png);;JPEG файлы (*.jpg);;PDF файлы (*.pdf);; SVG файлы (*.svg)")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            # Определяем формат на основе расширения файла
            if ext.lower().endswith(".png)"):
                if not file_extension:
                    file_name += ".png"
                self.figure.savefig(file_name, format="png")
            elif ext.lower().endswith(".jpg)"):
                if not file_extension:
                    file_name += ".jpg"
                self.figure.savefig(file_name, format="jpg")
            elif ext.lower().endswith(".pdf)"):
                if not file_extension:
                    file_name += ".pdf"
                self.figure.savefig(file_name, format="pdf")
            elif ext.lower().endswith(".svg)"):
                if not file_extension:
                    file_name += ".svg"
                self.figure.savefig(file_name, format="svg")
            else:
                self.figure.savefig(file_name)

    def copy_plot(self):
        """Копирование графика в буфер обмена."""
        # Создаем изображение из графика с тем же размером
        width, height = self.canvas.width(), self.canvas.height()
        image = QImage(width, height, QImage.Format.Format_ARGB32)

        # Рисуем на изображении с помощью QPainter
        painter = QPainter(image)
        self.canvas.render(painter)
        painter.end()

        # Копируем изображение в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

class WeibullPlot(QWidget):
    def __init__(self, shape_k, scale_lambda):
        super().__init__()

        self.shape_k = shape_k
        self.scale_lambda = scale_lambda

        self.setWindowTitle("График распределения Вейбулла")
        self.setGeometry(100, 100, 800, 600)

        # Создаем фигуру для графика
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Добавляем холст в макет
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Кнопки для сохранения и копирования графика
        self.save_button = QPushButton("Сохранить график")
        self.copy_button = QPushButton("Копировать график")
        self.save_button.clicked.connect(self.save_plot)
        self.copy_button.clicked.connect(self.copy_plot)

        layout.addWidget(self.save_button)
        layout.addWidget(self.copy_button)

        time_upper_limit = stats.weibull_min.ppf(0.99, c=float(shape_k), scale=float(self.scale_lambda))  # 99% охвата значений
        self.time = np.linspace(0, time_upper_limit, 1000)
        self.cdf_values = stats.weibull_min.cdf(self.time, c=float(shape_k), scale=float(self.scale_lambda))

        ax.plot(self.time, self.cdf_values, label="Функция распределения (CDF)", color="green")
        ax.set_title("Функция распределения (CDF)")
        ax.set_xlabel("Время до отказа")
        ax.set_ylabel("Вероятность")
        ax.grid()
        ax.legend()

        # Обновляем холст, чтобы отобразить график
        self.canvas.draw()

    def save_plot(self):
        """Сохранение графика в файл."""
        file_name, ext = QFileDialog.getSaveFileName(self, "Сохранить график", "",
                                                "PNG файлы (*.png);;JPEG файлы (*.jpg);;PDF файлы (*.pdf);; SVG файлы (*.svg)")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            # Определяем формат на основе расширения файла
            if ext.lower().endswith(".png)"):
                if not file_extension:
                    file_name += ".png"
                self.figure.savefig(file_name, format="png")
            elif ext.lower().endswith(".jpg)"):
                if not file_extension:
                    file_name += ".jpg"
                self.figure.savefig(file_name, format="jpg")
            elif ext.lower().endswith(".pdf)"):
                if not file_extension:
                    file_name += ".pdf"
                self.figure.savefig(file_name, format="pdf")
            elif ext.lower().endswith(".svg)"):
                if not file_extension:
                    file_name += ".svg"
                self.figure.savefig(file_name, format="svg")
            else:
                self.figure.savefig(file_name)

    def copy_plot(self):
        """Копирование графика в буфер обмена."""
        # Создаем изображение из графика с тем же размером
        width, height = self.canvas.width(), self.canvas.height()
        image = QImage(width, height, QImage.Format.Format_ARGB32)

        # Рисуем на изображении с помощью QPainter
        painter = QPainter(image)
        self.canvas.render(painter)
        painter.end()

        # Копируем изображение в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)


class WeibullReliabilityPlot(QWidget):
    def __init__(self, shape_k, scale_lambda):
        super().__init__()

        self.shape_k = shape_k
        self.scale_lambda = scale_lambda

        self.setWindowTitle("График вероятности безотказной работы (распределение Вейбулла)")
        self.setGeometry(100, 100, 800, 600)

        # Создаем фигуру для графика
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Добавляем холст в макет
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Кнопки для сохранения и копирования графика
        self.save_button = QPushButton("Сохранить график")
        self.copy_button = QPushButton("Копировать график")
        self.save_button.clicked.connect(self.save_plot)
        self.copy_button.clicked.connect(self.copy_plot)

        layout.addWidget(self.save_button)
        layout.addWidget(self.copy_button)

        time_upper_limit = stats.weibull_min.ppf(0.99, c=float(shape_k), scale=float(self.scale_lambda))  # 99% охвата значений
        self.time = np.linspace(0, time_upper_limit, 1000)
        self.cdf_values = stats.weibull_min.cdf(self.time, c=float(shape_k), scale=float(self.scale_lambda))
        self.reliability = 1 - self.cdf_values

        ax.plot(self.time, self.reliability, label="Надежность (R(t))", color="orange")
        ax.set_title("Вероятность безотказной работы (R(t))")
        ax.set_xlabel("Время до отказа (часы)")
        ax.set_ylabel("Надежность")
        ax.grid()
        ax.legend()

        # Обновляем холст, чтобы отобразить график
        self.canvas.draw()

    def save_plot(self):
        """Сохранение графика в файл."""
        file_name, ext = QFileDialog.getSaveFileName(self, "Сохранить график", "",
                                                "PNG файлы (*.png);;JPEG файлы (*.jpg);;PDF файлы (*.pdf);; SVG файлы (*.svg)")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            # Определяем формат на основе расширения файла
            if ext.lower().endswith(".png)"):
                if not file_extension:
                    file_name += ".png"
                self.figure.savefig(file_name, format="png")
            elif ext.lower().endswith(".jpg)"):
                if not file_extension:
                    file_name += ".jpg"
                self.figure.savefig(file_name, format="jpg")
            elif ext.lower().endswith(".pdf)"):
                if not file_extension:
                    file_name += ".pdf"
                self.figure.savefig(file_name, format="pdf")
            elif ext.lower().endswith(".svg)"):
                if not file_extension:
                    file_name += ".svg"
                self.figure.savefig(file_name, format="svg")
            else:
                self.figure.savefig(file_name)

    def copy_plot(self):
        """Копирование графика в буфер обмена."""
        # Создаем изображение из графика с тем же размером
        width, height = self.canvas.width(), self.canvas.height()
        image = QImage(width, height, QImage.Format.Format_ARGB32)

        # Рисуем на изображении с помощью QPainter
        painter = QPainter(image)
        self.canvas.render(painter)
        painter.end()

        # Копируем изображение в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)



class WeibullFailureRatePlot(QWidget):
    def __init__(self, shape_k, scale_lambda):
        super().__init__()

        self.shape_k = shape_k
        self.scale_lambda = scale_lambda

        self.setWindowTitle("График интенсивности отказов (распределение Вейбулла)")
        self.setGeometry(100, 100, 800, 600)

        # Создаем фигуру для графика
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Добавляем холст в макет
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Кнопки для сохранения и копирования графика
        self.save_button = QPushButton("Сохранить график")
        self.copy_button = QPushButton("Копировать график")
        self.save_button.clicked.connect(self.save_plot)
        self.copy_button.clicked.connect(self.copy_plot)

        layout.addWidget(self.save_button)
        layout.addWidget(self.copy_button)

        time_upper_limit = stats.weibull_min.ppf(0.99, c=float(shape_k), scale=float(self.scale_lambda))  # 99% охвата значений
        self.time = np.linspace(0, time_upper_limit, 1000)
        self.cdf_values = stats.weibull_min.cdf(self.time, c=float(shape_k), scale=float(self.scale_lambda))
        self.reliability = 1 - self.cdf_values
        self.pdf_values = stats.weibull_min.pdf(self.time, c=float(shape_k), scale=float(self.scale_lambda))
        self.failure_rate = self.pdf_values / self.reliability

        ax.plot(self.time, self.failure_rate, label="Интенсивность отказов (λ(t))", color="red")
        ax.set_title("Интенсивность отказов (λ(t))")
        ax.set_xlabel("Время до отказа (часы)")
        ax.set_ylabel("Интенсивность отказов")
        ax.set_ylim(0, max(self.failure_rate[~np.isinf(self.failure_rate)]))  # Исключить бесконечности
        ax.grid()
        ax.legend()

        # Обновляем холст, чтобы отобразить график
        self.canvas.draw()

    def save_plot(self):
        """Сохранение графика в файл."""
        file_name, ext = QFileDialog.getSaveFileName(self, "Сохранить график", "",
                                                "PNG файлы (*.png);;JPEG файлы (*.jpg);;PDF файлы (*.pdf);; SVG файлы (*.svg)")

        if file_name:
            _, file_extension = os.path.splitext(file_name)

            # Определяем формат на основе расширения файла
            if ext.lower().endswith(".png)"):
                if not file_extension:
                    file_name += ".png"
                self.figure.savefig(file_name, format="png")
            elif ext.lower().endswith(".jpg)"):
                if not file_extension:
                    file_name += ".jpg"
                self.figure.savefig(file_name, format="jpg")
            elif ext.lower().endswith(".pdf)"):
                if not file_extension:
                    file_name += ".pdf"
                self.figure.savefig(file_name, format="pdf")
            elif ext.lower().endswith(".svg)"):
                if not file_extension:
                    file_name += ".svg"
                self.figure.savefig(file_name, format="svg")
            else:
                self.figure.savefig(file_name)

    def copy_plot(self):
        """Копирование графика в буфер обмена."""
        # Создаем изображение из графика с тем же размером
        width, height = self.canvas.width(), self.canvas.height()
        image = QImage(width, height, QImage.Format.Format_ARGB32)

        # Рисуем на изображении с помощью QPainter
        painter = QPainter(image)
        self.canvas.render(painter)
        painter.end()

        # Копируем изображение в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)
