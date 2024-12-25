from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import (
    QLineEdit
)

class BaseLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            BaseLineEdit {
                border: 1px solid white;
                border-radius: 10px;
                padding: 0 8px;
                background: rgba(255, 255, 255, 0);
                selection-background-color: rgba(255, 255, 255, 0.5);
                color: white;
            }
            
            BaseLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5); /* Установить красный цвет с прозрачностью */
            }
            
            BaseLineEdit::read-only {
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)

    def change_color(self, color: str):
        self.setStyleSheet(f"""
            BaseLineEdit {{
                border: 1px solid white;
                border-radius: 10px;
                padding: 0 8px;
                background: rgba(255, 255, 255, 0);
                selection-background-color: rgba(255, 255, 255, 0.5);
                color: {color};
            }}
            
            BaseLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.5); /* Установить красный цвет с прозрачностью */
            }}
        """)


class FocusOutLineEdit(BaseLineEdit):
    # Сигнал, который будет испускаться при потере фокуса
    focusLost = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def focusOutEvent(self, event: QEvent):
        # Вызываем сигнал при потере фокуса
        self.focusLost.emit()
        super().focusOutEvent(event)