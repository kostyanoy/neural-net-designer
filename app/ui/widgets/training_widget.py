from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout


class TrainingWidget(QWidget):
    """Виджет настроек обучения (заглушка)"""

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