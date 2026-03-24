from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, \
    QSpinBox, QSlider, QCheckBox

from ui.dialog.message_boxes import choose_file_dataset, choose_dir_dataset


class DataWidget(QWidget):
    """Виджет настройки датасета"""

    dataset_config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_dataset_path = None
        self._current_dataset_type = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        dataset_group = self._create_dataset_group()
        layout.addWidget(dataset_group)

        preprocess_group = self._create_preprocessing_group()
        layout.addWidget(preprocess_group)

        layout.addStretch()

        return dataset_group

    def _create_dataset_group(self):
        dataset_group = QGroupBox("📊 Датасет")
        dataset_layout = QFormLayout()
        dataset_group.setLayout(dataset_layout)

        self.dataset_combo = QComboBox()
        self.dataset_combo.addItems([
            "Цветки Ириса",
            "MNIST",
            "Свой датасет"
        ])
        self.dataset_combo.currentIndexChanged.connect(self._on_dataset_changed)
        dataset_layout.addRow("Тип:", self.dataset_combo)

        self.dataset_label = QLabel("Не выбран")
        dataset_layout.addRow("Текущий:", self.dataset_label)

        self.select_file_btn = QPushButton("Из файла (CSV)")
        self.select_file_btn.clicked.connect(self._on_select_file_dataset)
        self.select_file_btn.setVisible(False)
        dataset_layout.addRow(self.select_file_btn)

        self.select_folder_btn = QPushButton("Из папки (Изображения)")
        self.select_folder_btn.clicked.connect(self._on_select_folder_dataset)
        self.select_folder_btn.setVisible(False)
        dataset_layout.addRow(self.select_folder_btn)

        return dataset_group

    def _create_preprocessing_group(self):
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
            self.dataset_label.setText("Не выбран")
            self._current_dataset_type = None
            self._current_dataset_path = None
        else:
            self.dataset_label.setText(dataset_text)
            self._current_dataset_type = dataset_text
            self._current_dataset_path = "preset"

        self.select_file_btn.setVisible(is_custom)
        self.select_folder_btn.setVisible(is_custom)
        self._on_change()

    def _on_select_file_dataset(self):
        """Выбор датасета из файла (CSV)"""
        path, _ = choose_file_dataset(self)
        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_file"
            filename = path.split('/')[-1].split('\\')[-1]
            self.dataset_label.setText(f"Файл: {filename}")
            self._on_change()

    def _on_select_folder_dataset(self):
        """Выбор датасета из папки (Изображения)"""
        path = choose_dir_dataset(self)

        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_folder"
            foldername = path.split('/')[-1].split('\\')[-1]
            self.dataset_label.setText(f"Папка: {foldername}")
            self._on_change()

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
        self.dataset_config_changed.emit()

    def clear_session(self):
        """Сбросить виджет датасета к начальному состоянию"""
        self._current_dataset_path = None
        self._current_dataset_type = None
        self.dataset_combo.setCurrentIndex(0)
        self.dataset_label.setText("Не выбран")
        self.select_file_btn.setVisible(False)
        self.select_folder_btn.setVisible(False)
        self.train_spin.setValue(80)
        self.split_slider.setValue(80)
        self.test_spin.setValue(20)
        self.stratify_check.setChecked(True)
        self.norm_combo.setCurrentText("Z-Score")
        self._on_change()

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
