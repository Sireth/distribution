from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QStyleOption, QStyle
)



class BaseSubstrate(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            BaseSubstrate {
                background-color: rgba(255, 255, 255, 0.15); /* Цвет фона */
                border-radius: 15px;      /* Радиус скругления */
            }
        """)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, a0):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)