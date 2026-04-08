from pathlib import Path

from PyQt5.QtWidgets import QMessageBox, QFileDialog

from config import PROJECTS_DIR


def save_changes_box(parent=None):
    """Диалог сохранения изменений перед созданием нового проекта."""
    return QMessageBox.question(
        parent,
        "Сохранить изменения",
        "Вы хотите сохранить изменения перед созданием нового проекта?",
        buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        defaultButton=QMessageBox.Save
    )


def choose_open_file(parent=None):
    """Диалог выбора файла проекта для открытия."""
    open_dir = Path(PROJECTS_DIR)
    open_dir.mkdir(parents=True, exist_ok=True)

    return QFileDialog.getOpenFileName(
        parent,
        "Открыть проект",
        directory=str(open_dir),
        filter="Project Files (*.nnd);;All files (*)"
    )


def choose_save_file(parent=None, name="Untitled"):
    """Диалог выбора файла для сохранения проекта."""
    save_dir = Path(PROJECTS_DIR)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = str(save_dir / f"{name}.nnd")

    return QFileDialog.getSaveFileName(
        parent,
        "Сохранить проект как",
        save_path,
        "Project Files (*.nnd);;All Files (*)"
    )


def choose_file_dataset(parent=None):
    """Диалог выбора CSV файла датасета."""
    return QFileDialog.getOpenFileName(
        parent,
        "Выберите CSV файл",
        "",
        "CSV Files (*.csv);;All Files (*)"
    )


def choose_dir_dataset(parent=None):
    """Диалог выбора папки с изображениями датасета."""
    return QFileDialog.getExistingDirectory(
        parent,
        "Выберите папку с изображениями"
    )

def choose_code_file(parent, name, types):
    """Диалог выбора файла для экспорта кода."""
    return QFileDialog.getSaveFileName(
        parent,
        "Сохранить код",
        name,
        types
    )

def choose_weights_file(parent=None):
    """Диалог выбора файла для экспорта весов модели."""
    return QFileDialog.getSaveFileName(
            parent,
            "Сохранить веса модели",
            "model_weights.pth",
            "PyTorch Weights (*.pth);;ONNX Model (*.onnx);;All Files (*)"
        )