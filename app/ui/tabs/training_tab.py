from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter

from ui.widgets.data_widget import DataWidget
from ui.widgets.training_widget import TrainingWidget


class TrainingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

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
