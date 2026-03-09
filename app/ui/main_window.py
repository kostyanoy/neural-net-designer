from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from app.config import APP_NAME, VERSION, WINDOW_WIDTH, WINDOW_HEIGHT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()