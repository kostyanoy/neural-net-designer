from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QFormLayout


class TrainingWidget(QWidget):
    """Виджет настроек обучения (заглушка)"""

    training_config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        train_group = QGroupBox("⚙️ Параметры обучения")
        train_layout = QFormLayout()

        train_layout.addRow("Оптимизатор:", QLabel("Adam (TODO)"))
        train_layout.addRow("Learning Rate:", QLabel("0.001 (TODO)"))
        train_layout.addRow("Batch Size:", QLabel("32 (TODO)"))
        train_layout.addRow("Эпохи:", QLabel("10 (TODO)"))

        train_group.setLayout(train_layout)
        layout.addWidget(train_group)

        layout.addStretch()

    def clear_session(self):
        """Сбросить параметры обучения к значениям по умолчанию"""
        # TODO Сброс к стандартным значениям

    def get_config(self) -> dict:
        return {
            "optimizer": "adam",  # TODO: реальные значения из UI
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10
        }

    def set_config(self, config: dict):
        """Восстановить конфигурацию обучения"""
        if not config:
            return
        # TODO

        self.training_config_changed.emit()
