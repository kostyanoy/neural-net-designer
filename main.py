import sys

from PyQt5.QtWidgets import QApplication

from app.config import APP_NAME, VERSION, APP_STYLES
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    # Применение стилей
    with open(APP_STYLES, 'r') as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
