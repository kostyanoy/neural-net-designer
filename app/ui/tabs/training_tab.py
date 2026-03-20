from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter

from core.project_manager import ProjectManager
from ui.widgets.data_widget import DataWidget
from ui.widgets.training_widget import TrainingWidget


class TrainingTab(QWidget):
    def __init__(self, parent, project_manager: ProjectManager):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()

        self.project_manager = project_manager

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter()
        splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)

        self.data_widget = DataWidget(self)
        self.training_widget = TrainingWidget(self)

        splitter.addWidget(self.data_widget)
        splitter.addWidget(self.training_widget)

        layout.addWidget(splitter)

    def _connect_signals(self):
        """Подключение сигналов для синхронизации свойств"""
        self.data_widget.dataset_config_changed.connect(self._on_config_changed)
        self.training_widget.config_changed.connect(self._on_config_changed)

    def _on_config_changed(self):
        """Обновление проекта"""
        self.project_manager.update_training_params(self.get_config())

    def clear_session(self):
        """Очистить вкладку"""
        self.data_widget.clear_session()
        self.training_widget.clear_session()

    def get_config(self):
        """Получить текущую конфигурацию обучения"""
        return {
            "dataset_config": self.data_widget.get_config(),
            "training_config": self.training_widget.get_config(),
        }

    def set_config(self, config):
        self.data_widget.set_config(config["dataset_config"])
        self.training_widget.set_config(config["training_config"])