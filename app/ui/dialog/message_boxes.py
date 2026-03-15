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
