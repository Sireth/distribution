from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QStyleOption, QStyle

from PyQt6.QtCore import Qt

from windows.base_substrate import BaseSubstrate
from windows.base_window import BaseWindow

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = BaseWindow()
    window.layout().addWidget(BaseSubstrate(window))
    window.show()
    sys.exit(app.exec())
