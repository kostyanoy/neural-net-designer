from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class ExportTab(QWidget):
    """Вкладка для экспорта кода модели и весов."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Вкладка 4: Экспорт (Export)\nЗдесь будет генерация кода и сохранение весов.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(label)