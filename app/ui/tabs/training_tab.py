from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class TrainingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # TODO
        label = QLabel(
            "Вкладка 2: Данные и Обучение (Data & Training)\nЗдесь будут настройки датасета и гиперпараметров.")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(label)
