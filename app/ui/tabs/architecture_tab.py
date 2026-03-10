from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel


class ArchitectureTab(QWidget):
    """Вкладка для визуального проектирования архитектуры нейросети."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # TODO
        label = QLabel("Вкладка 1: Архитектура (Architecture)\nЗдесь будет Canvas для блоков.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(label)