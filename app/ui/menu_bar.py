from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenuBar


class CustomMenuBar(QMenuBar):
    """Кастомная панель меню с сигнальной архитектурой для главного окна."""

    # Сигналы File
    new_project_triggered = pyqtSignal()
    open_project_triggered = pyqtSignal()
    save_project_triggered = pyqtSignal()
    export_triggered = pyqtSignal(str)
    settings_triggered = pyqtSignal()
    exit_triggered = pyqtSignal()

    # Сигналы Edit
    undo_triggered = pyqtSignal()
    redo_triggered = pyqtSignal()
    delete_triggered = pyqtSignal()
    select_all_triggered = pyqtSignal()

    # Сигналы View
    zoom_in_triggered = pyqtSignal()
    zoom_out_triggered = pyqtSignal()
    fit_screen_triggered = pyqtSignal()
    toggle_grid_triggered = pyqtSignal(bool)
    toggle_theme_triggered = pyqtSignal()
    toggle_left_dock_triggered = pyqtSignal()
    toggle_right_dock_triggered = pyqtSignal()

    # Сигналы Help
    docs_triggered = pyqtSignal()
    about_triggered = pyqtSignal()

    def __init__(self, parent=None):
        """Инициализация меню и создание всех пунктов."""
        super().__init__(parent)
        self._create_menus()

    def _create_menus(self):
        """Создает все основные категории меню (File, Edit, View, Help)."""
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        """Создает меню 'File' с действиями проекта и экспорта."""
        file_menu = self.addMenu("&File")

        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project_triggered.emit)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project_triggered.emit)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project_triggered.emit)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("&Export")

        export_model = QAction("Code: &Model", self)
        export_model.triggered.connect(lambda: self.export_triggered.emit("model"))
        export_menu.addAction(export_model)

        export_train = QAction("Code: &Training", self)
        export_train.triggered.connect(lambda: self.export_triggered.emit("training"))
        export_menu.addAction(export_train)

        export_test = QAction("Code: &Testing", self)
        export_test.triggered.connect(lambda: self.export_triggered.emit("testing"))
        export_menu.addAction(export_test)

        export_full = QAction("&Full Project (ZIP)", self)
        export_full.triggered.connect(lambda: self.export_triggered.emit("full"))
        export_menu.addAction(export_full)

        export_weights = QAction("&Weights (.pth/.onnx)", self)
        export_weights.triggered.connect(lambda: self.export_triggered.emit("weights"))
        export_menu.addAction(export_weights)

        file_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.settings_triggered.emit)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_triggered.emit)
        file_menu.addAction(exit_action)

    def _create_edit_menu(self):
        """Создает меню 'Edit' с действиями редактирования графа."""
        edit_menu = self.addMenu("&Edit")

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo_triggered.emit)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.redo_triggered.emit)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut("Del")
        self.delete_action.triggered.connect(self.delete_triggered.emit)
        edit_menu.addAction(self.delete_action)

        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self.select_all_triggered.emit)
        edit_menu.addAction(self.select_all_action)

    def _create_view_menu(self):
        """Создает меню 'View' с настройками отображения и темой."""
        view_menu = self.addMenu("&View")

        self.zoom_in = QAction("Zoom &In", self)
        self.zoom_in.setShortcut("Ctrl++")
        self.zoom_in.triggered.connect(self.zoom_in_triggered.emit)
        view_menu.addAction(self.zoom_in)

        self.zoom_out = QAction("Zoom &Out", self)
        self.zoom_out.setShortcut("Ctrl+-")
        self.zoom_out.triggered.connect(self.zoom_out_triggered.emit)
        view_menu.addAction(self.zoom_out)

        self.fit_screen = QAction("&Fit to Screen", self)
        self.fit_screen.setShortcut("Ctrl+0")
        self.fit_screen.triggered.connect(self.fit_screen_triggered.emit)
        view_menu.addAction(self.fit_screen)

        view_menu.addSeparator()

        self.grid_action = QAction("Toggle &Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.setShortcut("Ctrl+G")
        self.grid_action.toggled.connect(self.toggle_grid_triggered.emit)
        view_menu.addAction(self.grid_action)

        view_menu.addSeparator()

        self.left_dock_action = QAction("Show &Blocks Panel", self)
        self.left_dock_action.setShortcut("Ctrl+B")
        self.left_dock_action.setCheckable(True)
        self.left_dock_action.setChecked(True)
        self.left_dock_action.triggered.connect(self.toggle_left_dock_triggered.emit)
        view_menu.addAction(self.left_dock_action)

        self.right_dock_action = QAction("Show &Properties Panel", self)
        self.right_dock_action.setShortcut("Ctrl+P")
        self.right_dock_action.setCheckable(True)
        self.right_dock_action.setChecked(True)
        self.right_dock_action.triggered.connect(self.toggle_right_dock_triggered.emit)
        view_menu.addAction(self.right_dock_action)

        view_menu.addSeparator()

        theme_action = QAction("Toggle &Theme (Dark/Light)", self)
        theme_action.setShortcut("F2")
        theme_action.triggered.connect(self.toggle_theme_triggered.emit)
        view_menu.addAction(theme_action)

    def _create_help_menu(self):
        """Создает меню 'Help' с документацией и информацией о программе."""
        help_menu = self.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self.docs_triggered.emit)
        help_menu.addAction(docs_action)

        about_action = QAction("&About", self)
        about_action.setShortcut("Shift+F1")
        about_action.triggered.connect(self.about_triggered.emit)
        help_menu.addAction(about_action)

    def set_edit_actions_enabled(self, enabled: bool):
        """Включает или выключает действия меню Edit."""
        self.undo_action.setEnabled(enabled)
        self.redo_action.setEnabled(enabled)
        self.delete_action.setEnabled(enabled)
        self.select_all_action.setEnabled(enabled)

    def set_view_actions_enabled(self, enabled: bool):
        """Включает или выключает действия меню View."""
        self.zoom_in.setEnabled(enabled)
        self.zoom_out.setEnabled(enabled)
        self.fit_screen.setEnabled(enabled)
        self.grid_action.setEnabled(enabled)
        self.left_dock_action.setEnabled(enabled)
        self.right_dock_action.setEnabled(enabled)