from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QStyleOption, QStyle
)

from windows.base_line_edit import BaseLineEdit


class BaseWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setStyleSheet('''
        BaseWindow {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #e83a00,
                stop:1 #005ce8);
        }''')

        self.setLayout(QVBoxLayout())

    def paintEvent(self, a0):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def validate_number(self, input_num: BaseLineEdit):
        if input_num.text() == "":
            input_num.change_color("white")
            return False

        text = input_num.text()
        check = input_num.validator().validate(text, 0)[0]
        if check != QValidator.State.Acceptable:
            input_num.change_color("black")
            return False

        input_num.change_color("white")
        return True