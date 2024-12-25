from PyQt6.QtWidgets import (
    QPushButton
)



class BaseButton(QPushButton):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("""
            BaseButton {
                border: 1px solid white;
                border-radius: 8px;
                padding: 0 8px;
                background-color: rgba(255, 255, 255, 0);
                color: white;
            }
            
            BaseButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid white; /* Темный цвет границы при наведении */
            }
            
            BaseButton:!hover {
                background-color: rgba(255, 255, 255, 0);
                border: 1px solid white; /* Темный цвет границы при наведении */
            }
            
            /* Состояние при нажатии */
            BaseButton:pressed {
                background-color: rgba(255, 255, 255, 0.30);
                border: 2px solid white; /* Темный цвет границы при нажатии */
            }
            
            /* Состояние при фокусе (если кнопка фокусируется, например, с клавиатуры) */
            BaseButton:focus {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid white; /* Темный цвет границы при наведении */
            }
            
            /* Состояние, когда кнопка отключена */
            BaseButton:disabled {
                border-radius: 8px;
                padding: 0 8px;
                background-color: rgba(255, 255, 255, 0.1); /* Бледный фон */
                color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            
            /* Состояние, когда кнопка активна (всегда видно нажатие, когда кнопка активна) */
            BaseButton:active {
                border-radius: 8px;
                padding: 0 8px;
                border: 1px solid white;
                background-color: rgba(255, 255, 255, 0);
                color: white;
            }
            
            /* Состояние, когда кнопка в режиме "ховер" и нажата одновременно */
            BaseButton:hover:pressed {
                background-color: rgba(255, 255, 255, 0.30);
                border: 2px solid white; /* Темный цвет границы при нажатии */
            }
            
            /* Состояние, когда кнопка имеет фокус и нажата */
            BaseButton:focus:pressed {
                background-color: rgba(255, 255, 255, 0.30);
                border: 2px solid white; /* Темный цвет границы при нажатии */
            }
        """)
