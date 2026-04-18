from pathlib import Path

import torch
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, \
    QSpinBox, QSlider, QCheckBox
from sklearn import datasets as sklearn_datasets
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset
from torchvision import transforms, datasets

from ui.dialog.message_boxes import choose_file_dataset, choose_dir_dataset
from config import DATASETS_DIR


class DataWidget(QWidget):
    """Виджет настройки датасета"""

    dataset_valid = pyqtSignal(bool)
    dataset_config_changed = pyqtSignal()
    proceed_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_dataset_path = None
        self._current_dataset_type = None
        self._loaded_dataset = None
        self._loader_thread: QThread = None
        self._loader_worker: DatasetLoaderWorker = None
        self._init_ui()

    def _init_ui(self):
        """Инициализация UI элементов виджета датасета."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        dataset_group = self._create_dataset_group()
        layout.addWidget(dataset_group)

        preprocess_group = self._create_preprocessing_group()
        layout.addWidget(preprocess_group)

        layout.addStretch()

        return dataset_group

    def _create_dataset_group(self) -> QGroupBox:
        """Создание группы элементов выбора датасета."""
        dataset_group = QGroupBox("📊 Датасет")
        dataset_layout = QFormLayout()
        dataset_group.setLayout(dataset_layout)

        self.dataset_combo = QComboBox()
        self.dataset_combo.addItems([
            "Цветки Ириса",
            "MNIST",
            # "Свой датасет",
        ])
        self.dataset_combo.currentIndexChanged.connect(self._on_dataset_changed)
        dataset_layout.addRow("Тип:", self.dataset_combo)

        self.load_btn = QPushButton("Загрузить датасет")
        self.load_btn.clicked.connect(self._on_load_clicked)
        dataset_layout.addWidget(self.load_btn)

        self.dataset_label = QLabel("Не загружен")
        dataset_layout.addRow("Датасет:", self.dataset_label)

        self.select_file_btn = QPushButton("Из файла (CSV)")
        self.select_file_btn.clicked.connect(self._on_select_file_dataset)
        self.select_file_btn.setVisible(False)
        dataset_layout.addRow(self.select_file_btn)

        self.select_folder_btn = QPushButton("Из папки (Изображения)")
        self.select_folder_btn.clicked.connect(self._on_select_folder_dataset)
        self.select_folder_btn.setVisible(False)
        dataset_layout.addRow(self.select_folder_btn)

        self.next_btn = QPushButton("➡️ Далее: Мониторинг")
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.next_btn.setEnabled(False)
        dataset_layout.addWidget(self.next_btn)

        return dataset_group

    def _create_preprocessing_group(self) -> QGroupBox:
        """Создание группы элементов препроцессинга датасета."""
        preprocess_group = QGroupBox("🔧 Препроцессинг")
        preprocess_layout = QFormLayout()
        preprocess_group.setLayout(preprocess_layout)

        split_container = QWidget()
        split_layout = QHBoxLayout()
        split_container.setLayout(split_layout)

        self.train_spin = QSpinBox()
        self.train_spin.setRange(10, 90)
        self.train_spin.setValue(80)
        self.train_spin.setSuffix("%")
        self.train_spin.valueChanged.connect(self._on_split_changed)

        self.test_spin = QSpinBox()
        self.test_spin.setRange(10, 90)
        self.test_spin.setValue(20)
        self.test_spin.setSuffix("%")
        self.test_spin.setReadOnly(True)

        self.split_slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.split_slider.setRange(10, 90)
        self.split_slider.setValue(80)
        self.split_slider.valueChanged.connect(self._on_slider_changed)

        split_layout.addWidget(self.train_spin)
        split_layout.addWidget(self.split_slider)
        split_layout.addWidget(self.test_spin)
        preprocess_layout.addRow("Train/Test split:", split_container)

        self.stratify_check = QCheckBox()
        self.stratify_check.setChecked(True)
        self.stratify_check.stateChanged.connect(self._on_change)
        preprocess_layout.addRow("Стратификация:", self.stratify_check)

        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["None", "MinMax", "Z-Score"])
        self.norm_combo.currentIndexChanged.connect(self._on_change)
        preprocess_layout.addRow("Нормализация:", self.norm_combo)

        return preprocess_group

    def _on_dataset_changed(self, index):
        """Обработка изменения выбранного датасета"""
        dataset_text = self.dataset_combo.currentText()
        is_custom = "Свой датасет" in dataset_text

        if is_custom:
            self.load_btn.setVisible(False)
            self._current_dataset_type = None
            self._current_dataset_path = None
        else:
            self.load_btn.setVisible(True)
            self._current_dataset_type = dataset_text
            self._current_dataset_path = "preset"

        self.dataset_label.setText("Не загружен")
        self.select_file_btn.setVisible(is_custom)
        self.select_folder_btn.setVisible(is_custom)
        self._on_change()

    def _on_load_clicked(self):
        """Загрузка предзагруженного датасета"""
        if self._loader_thread and self._loader_thread.isRunning():
            return

        self.dataset_label.setText("Загружается...")
        self.set_dataset(None)
        self.load_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

        dataset_name = self.dataset_combo.currentText()
        train_split = self.train_spin.value()
        stratified = self.stratify_check.isChecked()
        norm_type = self.norm_combo.currentText()

        self._loader_worker = DatasetLoaderWorker(dataset_name, train_split, stratified, norm_type)
        self._loader_thread = QThread()

        self._loader_worker.moveToThread(self._loader_thread)
        self._loader_thread.started.connect(self._loader_worker.run)
        self._loader_worker.finished.connect(self._on_dataset_loaded)
        self._loader_worker.error.connect(self._on_dataset_load_error)
        self._loader_thread.finished.connect(self._loader_thread.deleteLater)
        self._loader_worker.finished.connect(self._loader_worker.deleteLater)

        self._loader_thread.start()

    def _on_dataset_loaded(self, dataset_info):
        """Обработка успешной загрузки датасета"""
        self.set_dataset(dataset_info)
        self.dataset_label.setText(f"Загружен - {dataset_info['name']}")
        self.next_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self._on_change()

        self._clear_thread()

    def _on_dataset_load_error(self, error_msg):
        """Обработка ошибки загрузки"""
        self.set_dataset(None)
        self.dataset_label.setText(f"Ошибка: {error_msg}")
        self.load_btn.setEnabled(True)
        self.next_btn.setEnabled(False)

        self._clear_thread()

    def _on_select_file_dataset(self):
        """Выбор датасета из файла (CSV)"""
        path, _ = choose_file_dataset(self)
        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_file"
            filename = Path(path).name
            self.dataset_label.setText(f"Файл: {filename}")
            self._on_change()

    def _on_select_folder_dataset(self):
        """Выбор датасета из папки (Изображения)"""
        path = choose_dir_dataset(self)

        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_folder"
            foldername = Path(path).name
            self.dataset_label.setText(f"Папка: {foldername}")
            self._on_change()

    def _on_next_clicked(self):
        """Переход на вкладку мониторинга"""
        self.proceed_requested.emit()

    def _on_split_changed(self, value):
        """Синхронизация слайдера и spinbox"""
        self.split_slider.setValue(value)
        self.test_spin.setValue(100 - value)
        self._on_change()

    def _on_slider_changed(self, value):
        """Синхронизация spinbox и слайдера"""
        self.train_spin.setValue(value)
        self.test_spin.setValue(100 - value)
        self._on_change()

    def _on_change(self):
        """Обработка изменений в настройках датасета."""
        self.dataset_config_changed.emit()

    def clear_session(self):
        """Сбросить виджет датасета к начальному состоянию"""
        self._clear_thread()

        self._current_dataset_path = None
        self._current_dataset_type = None
        self.set_dataset(None)
        self.dataset_combo.setCurrentIndex(0)
        self.dataset_label.setText("Не загружен")
        self.select_file_btn.setVisible(False)
        self.select_folder_btn.setVisible(False)
        self.train_spin.setValue(80)
        self.split_slider.setValue(80)
        self.test_spin.setValue(20)
        self.stratify_check.setChecked(True)
        self.norm_combo.setCurrentText("Z-Score")
        self.next_btn.setEnabled(False)
        self._on_change()

    def _clear_thread(self):
        """Очистка и завершение потока загрузки датасета."""
        if self._loader_thread and self._loader_thread.isRunning():
            self._loader_thread.quit()
            self._loader_thread.wait(1000)
            self._loader_thread = None
            self._loader_worker = None

    def get_config(self) -> dict:
        """Получить текущую конфигурацию датасета"""
        return {
            "type": self._current_dataset_type,
            "path": self._current_dataset_path,
            "combo_index": self.dataset_combo.currentIndex(),
            "train_split": self.train_spin.value(),
            "test_split": self.test_spin.value(),
            "stratified": self.stratify_check.isChecked(),
            "normalization": self.norm_combo.currentIndex()
        }

    def set_config(self, config: dict):
        """Восстановить конфигурацию датасета"""
        if not config:
            return

        combo_index = config.get("combo_index", 0)
        self.dataset_combo.setCurrentIndex(combo_index)

        dataset_type = config.get("type")
        dataset_path = config.get("path")

        if dataset_type and dataset_path:
            self._current_dataset_type = dataset_type
            self._current_dataset_path = dataset_path

            if dataset_type == "preset":
                dataset_name = self.dataset_combo.currentText()
                self.dataset_label.setText(dataset_name)
                self.select_file_btn.setVisible(False)
                self.select_folder_btn.setVisible(False)
            elif dataset_type == "custom_file":
                filename = dataset_path.split('/')[-1].split('\\')[-1]
                self.dataset_label.setText(f"Файл: {filename}")
                self.select_file_btn.setVisible(True)
                self.select_folder_btn.setVisible(True)
            elif dataset_type == "custom_folder":
                foldername = dataset_path.split('/')[-1].split('\\')[-1]
                self.dataset_label.setText(f"Папка: {foldername}")
                self.select_file_btn.setVisible(True)
                self.select_folder_btn.setVisible(True)

        train_value = config.get("train_split", 80)
        self.train_spin.setValue(train_value)
        self.test_spin.setValue(100 - train_value)
        self.split_slider.setValue(train_value)

        self.stratify_check.setChecked(config.get("stratified", True))
        self.norm_combo.setCurrentIndex(config.get("normalization", 0))

    def get_dataset(self):
        """Получить загруженный датасет"""
        return self._loaded_dataset

    def set_dataset(self, dataset):
        """Установить загруженный датасет."""
        if dataset is None:
            self.dataset_valid.emit(False)
        else:
            self.dataset_valid.emit(True)
        self._loaded_dataset = dataset


class DatasetLoaderWorker(QObject):
    """Фоновая загрузка датасета без блокировки UI."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, dataset_name: str, train_split: float, stratified: bool, norm_type: str):
        super().__init__()
        self.dataset_name = dataset_name
        self.train_split = train_split
        self.stratified = stratified
        self.norm_type = norm_type

    def run(self):
        """Запуск загрузки датасета в фоновом потоке."""
        try:
            if self.dataset_name == "MNIST":
                result = self._load_mnist_impl()
            elif self.dataset_name == "Цветки Ириса":
                result = self._load_iris_impl(self.train_split, self.stratified, self.norm_type)
            else:
                self.error.emit("Неизвестный тип датасета")
                return
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Ошибка загрузки: {str(e)}")

    @staticmethod
    def _load_mnist_impl():
        """Загрузка датасета MNIST."""
        Path(DATASETS_DIR).mkdir(exist_ok=True, parents=True)

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

        train_dataset = datasets.MNIST(root=DATASETS_DIR, train=True, download=True, transform=transform)
        test_dataset = datasets.MNIST(root=DATASETS_DIR, train=False, download=True, transform=transform)

        return {
            "name": "MNIST",
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "input_shape": (1, 28, 28),
            "num_classes": 10
        }

    @staticmethod
    def _load_iris_impl(train_split: float, stratified: bool, norm_type: str):
        """Загрузка датасета Iris с препроцессингом."""
        train_size = train_split / 100.0
        iris = sklearn_datasets.load_iris()

        X = iris.data
        y = iris.target
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            train_size=train_size,
            stratify=y if stratified else None,
        )

        norm_type = norm_type
        if norm_type == "Z-Score":
            mean = X_train.mean(axis=0)
            std = X_train.std(axis=0)
            X_train = (X_train - mean) / (std + 1e-8)
            X_test = (X_test - mean) / (std + 1e-8)
        elif norm_type == "MinMax":
            min_val = X_train.min(axis=0)
            max_val = X_train.max(axis=0)
            X_train = (X_train - min_val) / (max_val - min_val + 1e-8)
            X_test = (X_test - min_val) / (max_val - min_val + 1e-8)

        X_train_tensor = torch.FloatTensor(X_train)
        X_test_tensor = torch.FloatTensor(X_test)
        y_train_tensor = torch.LongTensor(y_train)
        y_test_tensor = torch.LongTensor(y_test)

        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

        return {
            "name": "Iris",
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "input_shape": (4,),
            "num_classes": 3
        }
