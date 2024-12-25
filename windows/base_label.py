from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QHBoxLayout, QStyleOption, QStyle, QLabel
)



class BaseLabel(QLabel):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("""
            BaseLabel {
                color: white; /* Цвет фона */
                background-color: rgba(255, 255, 255, 0); /* Цвет фона */
            }
        """)
