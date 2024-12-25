from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListView


class BaseListView(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.setStyleSheet("""
            BaseListView {
                background-color: rgba(255, 255, 255, 0);
                show-decoration-selected: 1; /* make the selection span the entire width of the view */
            }
            
            BaseListView:item {
                background: none;
                border-bottom: 1px solid white; /* Нижняя граница */
                margin: 0;
                padding: 10px;
                font-size: 16px;        /* Размер шрифта */
                font-weight: bold;      /* Жирный шрифт */
                line-height: 1.5;
            }
            
            BaseListView:item:selected {
                background: rgba(255, 255, 255, 0.15);
            }
            
            BaseListView:item:selected:!active {
                background: rgba(255, 255, 255, 0.15);
            }
            
            BaseListView:item:selected:active {
                background: rgba(255, 255, 255, 0.15);
            }
            
            BaseListView:item:hover {
                background: rgba(255, 255, 255, 0.15);
            }
            
            BaseListView:item:focus {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
