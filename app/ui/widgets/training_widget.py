import torch
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QSpinBox, QComboBox, QCheckBox, \
    QDoubleSpinBox, QListWidget


class TrainingWidget(QWidget):
    """Виджет настроек обучения"""

    training_config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._check_cuda()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.hyper_group = self._create_hyper_group()
        layout.addWidget(self.hyper_group)

        self.optim_group = self._create_optim_group()
        layout.addWidget(self.optim_group)

        layout.addStretch()

    def _create_hyper_group(self) -> QGroupBox:
        """Группа 1: Гиперпараметры"""
        group = QGroupBox("⚙️ Гиперпараметры")
        layout = QFormLayout()
        group.setLayout(layout)

        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(10)
        self.epochs_spin.valueChanged.connect(self._on_change)
        layout.addRow("Эпохи:", self.epochs_spin)

        self.batch_combo = QComboBox()
        self.batch_combo.addItems(["16", "32", "64", "128", "256", "512"])
        self.batch_combo.setCurrentText("32")
        self.batch_combo.currentTextChanged.connect(self._on_change)
        layout.addRow("Размер батча:", self.batch_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        self.device_combo.currentTextChanged.connect(self._on_change)
        layout.addRow("Device:", self.device_combo)

        self.shuffle_check = QCheckBox()
        self.shuffle_check.setChecked(True)
        self.shuffle_check.stateChanged.connect(self._on_change)
        layout.addRow("Перемешивание датасета:", self.shuffle_check)

        return group

    def _create_optim_group(self) -> QGroupBox:
        """Группа 2: Оптимизация"""
        group = QGroupBox("🎯 Оптимизация")
        layout = QFormLayout()
        group.setLayout(layout)

        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems(["Adam", "SGD", "AdamW", "RMSprop", "Adagrad"])
        self.optimizer_combo.currentTextChanged.connect(self._on_change)
        layout.addRow("Оптимизатор:", self.optimizer_combo)

        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.00001, 1.0)
        self.lr_spin.setSingleStep(0.0001)
        self.lr_spin.setValue(0.001)
        self.lr_spin.setDecimals(5)
        self.lr_spin.valueChanged.connect(self._on_change)
        layout.addRow("Скорость обучения:", self.lr_spin)

        self.wd_spin = QDoubleSpinBox()
        self.wd_spin.setRange(0.0, 1.0)
        self.wd_spin.setSingleStep(0.0001)
        self.wd_spin.setValue(0.0)
        self.wd_spin.setDecimals(5)
        self.wd_spin.valueChanged.connect(self._on_change)
        layout.addRow("L2-регуляризация:", self.wd_spin)

        self.loss_combo = QComboBox()
        self.loss_combo.addItems(["CrossEntropyLoss", "MSELoss", "BCELoss", "BCEWithLogitsLoss"])
        self.loss_combo.currentTextChanged.connect(self._on_change)
        layout.addRow("Функция потерь:", self.loss_combo)

        self.metrics_list = QListWidget()
        self.metrics_list.addItems(["Accuracy", "Precision", "Recall", "F1-Score"])
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            if i == 0:
                item.setCheckState(QtCore.Qt.CheckState.Checked)  # Только Accuracy по умолчанию
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.metrics_list.itemChanged.connect(self._on_change)
        self.metrics_list.setFixedSize(  # убрать пустое место
            self.metrics_list.width(),
            self.metrics_list.sizeHintForRow(0) * self.metrics_list.count() + 2 * self.metrics_list.frameWidth()
        )
        layout.addRow("Метрики:", self.metrics_list)

        return group

    def _check_cuda(self):
        """Проверка доступности CUDA"""
        self.cuda_available = torch.cuda.is_available()
        device_text = "cuda" if self.cuda_available else "cpu"
        self.device_combo.setCurrentText(device_text)
        self.device_combo.model().item(1).setEnabled(self.cuda_available)

    def _on_change(self):
        """Сигнал об изменении конфигурации"""
        self.training_config_changed.emit()

    def clear_session(self):
        """Сбросить параметры обучения к значениям по умолчанию"""
        self.epochs_spin.setValue(10)
        self.batch_combo.setCurrentText("32")
        self.device_combo.setCurrentText("cuda" if self.cuda_available else "cpu")
        self.shuffle_check.setChecked(True)
        self.optimizer_combo.setCurrentText("Adam")
        self.lr_spin.setValue(0.001)
        self.wd_spin.setValue(0.0)
        self.loss_combo.setCurrentText("CrossEntropyLoss")

        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if i == 0:
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.training_config_changed.emit()

    def get_config(self) -> dict:
        """Сбор текущих настроек в словарь"""
        metrics = []
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                metrics.append(item.text())

        return {
            "epochs": self.epochs_spin.value(),
            "batch_size": int(self.batch_combo.currentText()),
            "device": self.device_combo.currentText(),
            "shuffle": self.shuffle_check.isChecked(),
            "optimizer": self.optimizer_combo.currentText(),
            "learning_rate": self.lr_spin.value(),
            "weight_decay": self.wd_spin.value(),
            "loss_function": self.loss_combo.currentText(),
            "metrics": metrics
        }

    def set_config(self, config: dict):
        """Восстановить конфигурацию обучения"""
        if not config:
            return

        self.epochs_spin.setValue(config.get("epochs", 10))
        self.batch_combo.setCurrentText(str(config.get("batch_size", 32)))
        self.device_combo.setCurrentText(config.get("device", "cpu"))
        self.shuffle_check.setChecked(config.get("shuffle", True))
        self.optimizer_combo.setCurrentText(config.get("optimizer", "Adam"))
        self.lr_spin.setValue(config.get("learning_rate", 0.001))
        self.wd_spin.setValue(config.get("weight_decay", 0.0))
        self.loss_combo.setCurrentText(config.get("loss_function", "CrossEntropyLoss"))

        metrics = config.get("metrics", ["Accuracy"])
        for i in range(self.metrics_list.count()):
            item = self.metrics_list.item(i)
            if item.text() in metrics:
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.training_config_changed.emit()
