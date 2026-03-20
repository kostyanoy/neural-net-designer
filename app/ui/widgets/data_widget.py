from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton, QComboBox

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

        dataset_group = QGroupBox("📊 Датасет")
        dataset_layout = QFormLayout()

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

        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)

        preprocess_group = QGroupBox("🔧 Препроцессинг")
        preprocess_layout = QVBoxLayout()
        preprocess_layout.addWidget(QLabel("Split: (TODO)"))
        preprocess_group.setLayout(preprocess_layout)
        layout.addWidget(preprocess_group)

        layout.addStretch()

        return dataset_group

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
        self.dataset_config_changed.emit()

    def _on_select_file_dataset(self):
        """Выбор датасета из файла (CSV)"""
        path, _ = choose_file_dataset(self)
        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_file"
            filename = path.split('/')[-1].split('\\')[-1]
            self.dataset_label.setText(f"Файл: {filename}")
            self.dataset_config_changed.emit()

    def _on_select_folder_dataset(self):
        """Выбор датасета из папки (Изображения)"""
        path = choose_dir_dataset(self)

        if path:
            self._current_dataset_path = path
            self._current_dataset_type = "custom_folder"
            foldername = path.split('/')[-1].split('\\')[-1]
            self.dataset_label.setText(f"Папка: {foldername}")
            self.dataset_config_changed.emit()

    def clear_session(self):
        """Сбросить виджет датасета к начальному состоянию"""
        self._current_dataset_path = None
        self._current_dataset_type = None
        self.dataset_combo.setCurrentIndex(0)
        self.dataset_label.setText("Не выбран")
        self.select_file_btn.setVisible(False)
        self.select_folder_btn.setVisible(False)
        self.dataset_config_changed.emit()

    def get_config(self) -> dict:
        """Получить текущую конфигурацию датасета"""
        return {
            "type": self._current_dataset_type,
            "path": self._current_dataset_path,
            "combo_index": self.dataset_combo.currentIndex()
        }

    def set_config(self, config: dict):
        """Восстановить конфигурацию датасета"""
        if not config:
            return

        combo_index = config.get("combo_index", 0)
        self.dataset_combo.setCurrentIndex(combo_index)

        dataset_type = config.get("type")
        dataset_path = config.get("path")

        if not (dataset_type and dataset_path):
            return

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
