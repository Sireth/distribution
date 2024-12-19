from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QListView,
)

from windows.poisson.poisson_window import PoissonWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Distribution")
        self.resize(800, 600)

        self.setCentralWidget(QWidget())

        # Основная сетка
        grid = QGridLayout()
        self.centralWidget().setLayout(grid)

        # Список распределений
        self.distribution_list = QListView()
        grid.addWidget(self.distribution_list, 0, 0)

        # Модель для списка
        self.distribution_model = QStandardItemModel()
        self.distribution_list.setModel(self.distribution_model)

        # Добавление элементов
        distributions = [
            "Распределение Пуассона",
            "Distribution 2",
            "Distribution 3",
            "Distribution 4",
            "Distribution 5",
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

                # window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # Освобождаем память при закрытии
            # case 1:
            #     from windows.bernoulli_window import BernoulliWindow
            #     dialog = BernoulliWindow(self)
            # case 2:
            #     from windows.geometric_window import GeometricWindow
            #     dialog = GeometricWindow(self)
            # case 3:
            #     from windows.binomial_window import BinomialWindow
            #     dialog = BinomialWindow(self)
            # case 4:
            #     from windows.hypergeometric_window import HypergeometricWindow
            #     dialog = HypergeometricWindow(self)
            # case _:

        window.show()
