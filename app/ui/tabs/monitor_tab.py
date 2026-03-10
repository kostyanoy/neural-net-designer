from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class MonitorTab(QWidget):
    """Вкладка для запуска обучения и мониторинга метрик в реальном времени."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Вкладка 3: Запуск и Результаты (Run & Monitor)\nЗдесь будут графики Loss/Accuracy и логи.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(label)