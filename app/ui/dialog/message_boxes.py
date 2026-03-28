from PyQt5.QtWidgets import QMessageBox, QFileDialog


def save_changes_box(parent=None):
    return QMessageBox.question(
        parent,
        "Сохранить изменения",
        "Вы хотите сохранить изменения перед созданием нового проекта?",
        buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        defaultButton=QMessageBox.Save
    )


def choose_open_file(parent=None):
    return QFileDialog.getOpenFileName(
        parent,
        "Открыть проект",
        filter="Project Files (*.nnd);;All files (*)"
    )


def choose_save_file(parent=None, name="Untitled"):
    return QFileDialog.getSaveFileName(
        parent,
        "Сохранить проект как",
        f"{name}.nnd",
        "Project Files (*.nnd);;All Files (*)"
    )


def choose_file_dataset(parent=None):
    return QFileDialog.getOpenFileName(
        parent,
        "Выберите CSV файл",
        "",
        "CSV Files (*.csv);;All Files (*)"
    )


def choose_dir_dataset(parent=None):
    return QFileDialog.getExistingDirectory(
        parent,
        "Выберите папку с изображениями"
    )

def choose_code_file(parent, name, types):
    return QFileDialog.getSaveFileName(
        parent,
        "Сохранить код",
        name,
        types
    )

def choose_weights_file(parent=None):
    return QFileDialog.getSaveFileName(
            parent,
            "Сохранить веса модели",
            "model_weights.pth",
            "PyTorch Weights (*.pth);;ONNX Model (*.onnx);;All Files (*)"
        )