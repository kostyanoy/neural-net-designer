import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.config import APP_NAME, VERSION, APP_STYLES


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    # Применение стилей
    with open(APP_STYLES, 'r') as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()