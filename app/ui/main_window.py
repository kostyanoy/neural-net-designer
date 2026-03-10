from PyQt6.QtWidgets import QMainWindow, QStatusBar, QTabWidget

from config import APP_NAME
from ui.menu_bar import CustomMenuBar
from ui.tabs import ArchitectureTab, TrainingTab, MonitorTab, ExportTab


class MainWindow(QMainWindow):
    """Главное окно приложения, управляющее меню, статусом и центральной областью."""

    def __init__(self):
        """Инициализация главного окна и подключение компонентов."""
        super().__init__()

        self.setWindowTitle(APP_NAME)

        self._init_menu()
        self._init_status_bar()
        self._init_tabs()
        self._connect_signals()

    def _init_menu(self):
        """Создание и установка Menu Bar."""
        self.menu_bar = CustomMenuBar(self)
        self.setMenuBar(self.menu_bar)

    def _init_status_bar(self):
        """Создание Status Bar с начальным сообщением."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _init_tabs(self):
        """Создание центральной области-заглушки до реализации вкладок."""
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.architecture_tab = ArchitectureTab(self)
        self.training_tab = TrainingTab(self)
        self.monitor_tab = MonitorTab(self)
        self.export_tab = ExportTab(self)

        self.tab_widget.addTab(self.architecture_tab, "🏗️ Архитектура")
        self.tab_widget.addTab(self.training_tab, "⚙️ Обучение")
        self.tab_widget.addTab(self.monitor_tab, "📊 Мониторинг")
        self.tab_widget.addTab(self.export_tab, "💾 Экспорт")

        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _connect_signals(self):
        """Подключение всех сигналов меню к соответствующим слотам-заглушкам."""
        # --- File ---
        self.menu_bar.new_project_triggered.connect(self._on_new_project)
        self.menu_bar.open_project_triggered.connect(self._on_open_project)
        self.menu_bar.save_project_triggered.connect(self._on_save_project)
        self.menu_bar.export_triggered.connect(self._on_export)
        self.menu_bar.settings_triggered.connect(self._on_settings)
        self.menu_bar.exit_triggered.connect(self.close)

        # --- Edit ---
        self.menu_bar.undo_triggered.connect(self._on_undo)
        self.menu_bar.redo_triggered.connect(self._on_redo)
        self.menu_bar.delete_triggered.connect(self._on_delete)
        self.menu_bar.select_all_triggered.connect(self._on_select_all)

        # --- View ---
        self.menu_bar.zoom_in_triggered.connect(self._on_zoom_in)
        self.menu_bar.zoom_out_triggered.connect(self._on_zoom_out)
        self.menu_bar.fit_screen_triggered.connect(self._on_fit_screen)
        self.menu_bar.toggle_grid_triggered.connect(self._on_toggle_grid)
        self.menu_bar.toggle_theme_triggered.connect(self._toggle_theme)

        # --- Help ---
        self.menu_bar.docs_triggered.connect(self._on_docs)
        self.menu_bar.about_triggered.connect(self._show_about)

    def _on_tab_changed(self, index: int):
        """Обработка переключения между вкладками."""
        # TODO
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Active Tab: {tab_name}")

    # --- Слоты: File ---

    def _on_new_project(self):
        """Обработка создания нового проекта."""
        # TODO
        self.status_bar.showMessage("Action: New Project")
        print("Creating new project...")

    def _on_open_project(self):
        """Обработка открытия существующего проекта."""
        # TODO
        self.status_bar.showMessage("Action: Open Project")
        print("Opening project dialog...")

    def _on_save_project(self):
        """Обработка сохранения текущего проекта."""
        # TODO
        self.status_bar.showMessage("Action: Save Project")
        print("Saving project...")

    def _on_export(self, export_type: str):
        """Обработка экспорта (код, веса, проект)."""
        # TODO
        self.status_bar.showMessage(f"Action: Export {export_type}")
        print(f"Exporting: {export_type}")

    def _on_settings(self):
        """Обработка открытия настроек приложения."""
        # TODO
        self.status_bar.showMessage("Action: Settings")
        print("Opening settings...")

    # --- Слоты: Edit ---

    def _on_undo(self):
        """Обработка отмены последнего действия."""
        # TODO
        self.status_bar.showMessage("Action: Undo")
        print("Undo requested")

    def _on_redo(self):
        """Обработка повтора отмененного действия."""
        # TODO
        self.status_bar.showMessage("Action: Redo")
        print("Redo requested")

    def _on_delete(self):
        """Обработка удаления выбранных элементов."""
        # TODO
        self.status_bar.showMessage("Action: Delete")
        print("Delete requested")

    def _on_select_all(self):
        """Обработка выделения всех элементов на канвасе."""
        # TODO
        self.status_bar.showMessage("Action: Select All")
        print("Select All requested")

    # --- Слоты: View ---

    def _on_zoom_in(self):
        """Обработка увеличения масштаба канваса."""
        # TODO
        self.status_bar.showMessage("Action: Zoom In")
        print("Zoom In requested")

    def _on_zoom_out(self):
        """Обработка уменьшения масштаба канваса."""
        # TODO
        self.status_bar.showMessage("Action: Zoom Out")
        print("Zoom Out requested")

    def _on_fit_screen(self):
        """Обработка подгонки содержимого под размер окна."""
        # TODO
        self.status_bar.showMessage("Action: Fit to Screen")
        print("Fit to Screen requested")

    def _on_toggle_grid(self, is_checked: bool):
        """Обработка переключения видимости сетки."""
        # TODO
        # Получаем состояние чекбокса из отправителя сигнала (если нужно)
        state = "ON" if is_checked else "OFF"
        self.status_bar.showMessage(f"Action: Toggle Grid ({state})")
        print(f"Toggle Grid: {state}")

    def _toggle_theme(self):
        """Обработка переключения темы (Dark/Light)."""
        # TODO
        self.status_bar.showMessage("Action: Toggle Theme")
        print("Theme toggle requested")

    # --- Слоты: Help ---

    def _on_docs(self):
        """Обработка открытия документации."""
        # TODO
        self.status_bar.showMessage("Action: Open Documentation")
        print("Documentation requested")

    def _show_about(self):
        """Обработка отображения окна 'О программе'."""
        # TODO
        self.status_bar.showMessage("Action: About")
        print(f"About {APP_NAME}")
