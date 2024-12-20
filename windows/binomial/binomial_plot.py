import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PyQt6.QtGui import QPainter, QImage
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
import scipy.stats as stats

class BinomialDensityPlot(QWidget):
    def __init__(self, n, p, q):
        super().__init__()

        self.setWindowTitle("График плотности Биномиального распределения")
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

        self.k_values = np.arange(0, n + 1)
        self.pmf_values = stats.binom.pmf(self.k_values, n, float(p))

        ax.bar(self.k_values, self.pmf_values, color="blue", alpha=0.7, label="Теоретическое распределение")

        ax.set_title(f"Плотность Биномиального распределения (n={n}, p={p}, q={q})")
        ax.set_xlabel("Количество событий")
        ax.set_ylabel("Вероятность")

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

class BinomialPlot(QWidget):
    def __init__(self, n, p, q):
        super().__init__()

        self.setWindowTitle("График Биномиального распределения")
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

        self.k_values = np.arange(0, n + 1)
        self.pmf_values = stats.binom.cdf(self.k_values, n, float(p))

        ax.bar(self.k_values, self.pmf_values, color="blue", alpha=0.7, label="Теоретическое распределение")

        ax.set_title(f"Биномиальное распределения (n={n}, p={p}, q={q})")
        ax.set_xlabel("Количество событий")
        ax.set_ylabel("Вероятность")

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
