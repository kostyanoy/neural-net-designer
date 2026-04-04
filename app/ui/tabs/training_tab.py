import torch
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from torch import nn
from torch.utils.data import DataLoader

from core.project_manager import ProjectManager
from ui.widgets.data_widget import DataWidget
from ui.widgets.training_widget import TrainingWidget


class TrainingTab(QWidget):

    proceed_requested = pyqtSignal()

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

        splitter.setSizes([1000, 1000])

        layout.addWidget(splitter)

    def _connect_signals(self):
        """Подключение сигналов для синхронизации свойств"""
        self.data_widget.dataset_config_changed.connect(self._on_config_changed)
        self.training_widget.training_config_changed.connect(self._on_config_changed)
        self.data_widget.proceed_requested.connect(lambda: self.proceed_requested.emit())

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
        self.clear_session()
        self.data_widget.set_config(config["dataset_config"])
        self.training_widget.set_config(config["training_config"])

    def get_training_object(self, model: nn.Module):
        """Вернуть объект со всеми необходимыми данными для запуска обучения."""
        dataset_info = self.data_widget.get_dataset()
        training_params = self.training_widget.get_config()

        if dataset_info is None:
            return None

        train_loader = DataLoader(dataset_info["train_dataset"], batch_size=training_params["batch_size"], shuffle=True)
        test_loader = DataLoader(dataset_info["test_dataset"], batch_size=training_params["batch_size"], shuffle=False)

        device = torch.device(training_params["device"])
        model = model.to(device)

        optimizer = self.training_widget.create_optimizer(model.parameters())
        loss_fn = self.training_widget.create_loss_function()

        return {
            "dataset": dataset_info,
            "train_loader": train_loader,
            "test_loader": test_loader,
            "model": model,
            "optimizer": optimizer,
            "loss_fn": loss_fn,
            "params": training_params,
            "device": device,
        }

