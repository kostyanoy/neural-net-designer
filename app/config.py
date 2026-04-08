from pathlib import Path

APP_NAME = "NeuralNet Designer"
VERSION = "0.1.0"
ORGANIZATION = "ITMO"
AUTHOR = "Манухин Константин"

# Пути
APP_STYLES = str(Path(__file__).parent.parent / "app" / "styles.qss")
PROJECTS_DIR = str(Path(__file__).parent.parent / "data" / "projects")
DATASETS_DIR = str(Path(__file__).parent.parent / "data" / "datasets")
TEMPLATES_DIR = str(Path(__file__).parent.parent / "app" / "templates")

# Настройки
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
DEFAULT_THEME = "dark"
AUTO_SAVE = True
MAX_UNDO_STEPS = 50

# Backend
DEFAULT_BACKEND = "pytorch"
SUPPORTED_DEVICES = ["cpu", "cuda"]