from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton, QComboBox, QFileDialog

from ui.dialog.message_boxes import choose_file_dataset, choose_dir_dataset


class DataWidget(QWidget):
    """Виджет настройки датасета"""

    dataset_loaded = pyqtSignal(str, str)  # (dataset_type, path)

    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.load_btn = QPushButton("Загрузить датасет")
        self.load_btn.clicked.connect(self._on_load_preset_dataset)
        dataset_layout.addRow(self.load_btn)

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

        self.load_btn.setVisible(not is_custom)
        self.select_file_btn.setVisible(is_custom)
        self.select_folder_btn.setVisible(is_custom)

        self.dataset_label.setText("Не выбран")
        self._current_dataset_path = None

        print(f"Dataset type changed: {dataset_text}")

    def _on_load_preset_dataset(self):
        """Загрузка готового датасета"""
        dataset_type = self.dataset_combo.currentText()
        self.dataset_label.setText(f"Загрузка: {dataset_type}")
        self._current_dataset_path = "preset"
        self.dataset_loaded.emit(dataset_type, "preset")
        print(f"Loading preset dataset: {dataset_type}")

    def _on_select_file_dataset(self):
        """Выбор датасета из файла (CSV)"""
        path, _ = choose_file_dataset(self)
        if path:
            self._current_dataset_path = path
            self.dataset_label.setText(f"Файл: {path.split('/')[-1]}")
            self.dataset_loaded.emit("custom_file", path)
            print(f"Custom file dataset selected: {path}")

    def _on_select_folder_dataset(self):
        """Выбор датасета из папки (Изображения)"""
        path = choose_dir_dataset(self)

        if path:
            self._current_dataset_path = path
            self.dataset_label.setText(f"Папка: {path.split('/')[-1]}")
            self.dataset_loaded.emit("custom_folder", path)
            print(f"Custom folder dataset selected: {path}")