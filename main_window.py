from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout,
)

from windows.base_list_view import BaseListView
from windows.binomial.binomial_window import BinomialWindow
from windows.expon.expon_window import ExponWindow
from windows.normal.normal_window import NormalWindow
from windows.poisson.poisson_window import PoissonWindow
from windows.weibull.weibull_window import WeibullWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Distribution")
        self.setStyleSheet('''
                MainWindow {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #e83a00,
                        stop:1 #005ce8);
                }''')
        self.resize(800, 600)

        self.setCentralWidget(QWidget(self))

        # Основная сетка
        grid = QGridLayout()
        self.centralWidget().setLayout(grid)

        # Список распределений
        self.distribution_list = BaseListView(self)
        grid.addWidget(self.distribution_list, 0, 0)

        # Модель для списка
        self.distribution_model = QStandardItemModel()
        self.distribution_list.setModel(self.distribution_model)

        # Добавление элементов
        distributions = [
            "Распределение Пуассона",
            "Биномиальное распределение",
            "Нормальное распределение",
            "Экспоненциальное распределение",
            "Распределение Вейбулла",
        ]
        for distribution in distributions:
            item = QStandardItem(distribution)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Только выбор и включение
            self.distribution_model.appendRow(item)


        # Подключение сигнала двойного нажатия
        self.distribution_list.doubleClicked.connect(self.open_distribution_window)


    def open_distribution_window(self, index):
        # Получение текста выбранного элемента
        distribution_id = self.distribution_model.itemFromIndex(index).row()

        match distribution_id:
            case 0:
                window = PoissonWindow()
            case 1:
                window = BinomialWindow()
            case 2:
                window = NormalWindow()
            case 3:
                window = ExponWindow()
            case 4:
                window = WeibullWindow()
            case _:
                return
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        window.show()
