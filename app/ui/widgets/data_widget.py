from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QPushButton


class DataWidget(QWidget):
    """Виджет настройки датасета"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        dataset_group = QGroupBox("📊 Датасет")
        dataset_layout = QFormLayout()

        self.dataset_label = QLabel("Не выбран")
        dataset_layout.addRow("Текущий:", self.dataset_label)

        self.load_btn = QPushButton("Загрузить датасет")
        dataset_layout.addRow(self.load_btn)

        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)

        preprocess_group = QGroupBox("🔧 Препроцессинг")
        preprocess_layout = QVBoxLayout()
        preprocess_layout.addWidget(QLabel("Split: (TODO)"))
        preprocess_group.setLayout(preprocess_layout)
        layout.addWidget(preprocess_group)

        layout.addStretch()

        return dataset_group