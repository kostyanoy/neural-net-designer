import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.config import APP_NAME, VERSION


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    # Применение стилей
    with open('app/styles.qss', 'r') as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()