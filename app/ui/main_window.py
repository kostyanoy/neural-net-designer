from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QMessageBox

from config import APP_NAME
from core.project_manager import ProjectManager
from ui.dialog.message_boxes import save_changes_box, choose_open_file, choose_save_file
from ui.menu_bar import CustomMenuBar
from ui.tabs import ArchitectureTab, TrainingTab, MonitorTab, ExportTab


class MainWindow(QMainWindow):
    """Главное окно приложения, управляющее меню, статусом и центральной областью."""

    def __init__(self):
        """Инициализация главного окна и подключение компонентов."""
        super().__init__()

        self.project_manager = ProjectManager()
        self._modified = False

        self.setWindowTitle(APP_NAME)

        self._init_menu()
        self._init_status_bar()
        self._init_tabs()
        self._init_docks()
        self._connect_signals()
        self._init_project()

    def _init_menu(self):
        """Создание и установка Menu Bar."""
        self.menu_bar = CustomMenuBar(self)
        self.setMenuBar(self.menu_bar)

    def _init_status_bar(self):
        """Создание Status Bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _init_tabs(self):
        """Создание вкладок."""
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.architecture_tab = ArchitectureTab(self, self.project_manager)
        self.training_tab = TrainingTab(self, self.project_manager)
        self.monitor_tab = MonitorTab(self)
        self.export_tab = ExportTab(self)

        self.tab_widget.addTab(self.architecture_tab, "🏗️ Архитектура")
        self.tab_widget.addTab(self.training_tab, "⚙️ Обучение")
        self.tab_widget.addTab(self.monitor_tab, "📊 Мониторинг")
        self.tab_widget.addTab(self.export_tab, "💾 Экспорт")

    def _init_docks(self):
        """Подключение Dock"""
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.architecture_tab.left_dock)
        self.left_dock = self.architecture_tab.left_dock

        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.architecture_tab.right_dock)
        self.right_dock = self.architecture_tab.right_dock

    def _connect_signals(self):
        """Подключение всех сигналов меню к соответствующим слотам."""
        # --- File ---
        self.menu_bar.new_project_triggered.connect(self._on_new_project)
        self.menu_bar.open_project_triggered.connect(self._on_open_project)
        self.menu_bar.save_project_triggered.connect(self._on_save_project)
        self.menu_bar.save_project_as_triggered.connect(self._on_save_project_as)
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
        self.menu_bar.toggle_left_dock_triggered.connect(self._toggle_left_dock)
        self.menu_bar.toggle_right_dock_triggered.connect(self._toggle_right_dock)

        # --- Help ---
        self.menu_bar.docs_triggered.connect(self._on_docs)
        self.menu_bar.about_triggered.connect(self._show_about)

        # --- Dock ---
        self.left_dock.visibilityChanged.connect(self._on_dock_visibility_changed)
        self.right_dock.visibilityChanged.connect(self._on_dock_visibility_changed)

        # --- Tab ---
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # --- Architecture Tab ---
        self.architecture_tab.graph.node_selected.connect(self._on_node_selected)

        # --- Project Manager ---
        self.project_manager.project_loaded.connect(self._on_project_loaded)
        self.project_manager.project_saved.connect(self._on_project_saved)
        self.project_manager.project_changed.connect(self._on_project_changed)

    def _init_project(self):
        self.project_manager.create_new_project()

    # --- Слоты: File ---

    def _on_new_project(self):
        """Обработка создания нового проекта."""
        if self._modified:
            reply = save_changes_box(self)
            if reply == QMessageBox.Save:
                self._on_save_project()
            elif reply == QMessageBox.Cancel:
                return

        self.project_manager.create_new_project()
        self.architecture_tab.graph.clear_session()
        self.training_tab.clear_session()
        self.status_bar.showMessage("Создан новый проект")

    def _on_open_project(self):
        """Обработка открытия существующего проекта."""
        if self._modified:
            reply = save_changes_box(self)
            if reply == QMessageBox.Save:
                self._on_save_project()
            elif reply == QMessageBox.Cancel:
                return

        path, _ = choose_open_file(self)
        if path:
            project_data = self.project_manager.load_project(path)
            self.architecture_tab.deserialize_graph(project_data["architecture"])
            self.training_tab.set_config(project_data["training"])

            self.status_bar.showMessage(f"Загружен проект из файла: {path}")

    def _on_save_project(self):
        """Обработка сохранения текущего проекта."""
        if self.project_manager.project_path:
            path = self.project_manager.project_path
            self.project_manager.save_project(self.project_manager.project_path,
                                              self.architecture_tab.serialize_graph(),
                                              self.training_tab.get_config())
            self.status_bar.showMessage(f"Проект сохранен в файл: {path}")
        else:
            self._on_save_project_as()

    def _on_save_project_as(self):  # ← ДОБАВИТЬ новый метод
        """Обработка сохранения проекта как..."""
        path, _ = choose_save_file(self, self.project_manager.get_project_name())
        if path:
            if not path.endswith(".nnd"):
                path += ".nnd"
            name = Path(path).stem
            self.project_manager.set_project_name(name)
            self.project_manager.project_path = path
            self._on_save_project()

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

    def _toggle_left_dock(self):
        """Переключение видимости левой панели."""
        self.left_dock.setVisible(not self.left_dock.isVisible())

    def _toggle_right_dock(self):
        """Переключение видимости правой панели."""
        self.right_dock.setVisible(not self.right_dock.isVisible())

    def _on_dock_visibility_changed(self, visible: bool):
        """Синхронизация состояния чекбоксов в меню с видимостью панелей."""
        self.menu_bar.left_dock_action.setChecked(self.left_dock.isVisible())
        self.menu_bar.right_dock_action.setChecked(self.right_dock.isVisible())

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

    def _on_tab_changed(self, index: int):
        """Обработка переключения между вкладками."""
        # TODO
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Active Tab: {tab_name}")

        is_architecture_tab = (index == 0)
        is_training_tab = (index == 1)
        is_monitor_tab = (index == 2)
        is_export_tab = (index == 3)

        self.menu_bar.set_edit_actions_enabled(is_architecture_tab)
        self.menu_bar.set_view_actions_enabled(is_architecture_tab)

        self.left_dock.setVisible(is_architecture_tab)
        self.right_dock.setVisible(is_architecture_tab)

        if is_monitor_tab:
            training = self.training_tab.get_config()
            metrics = training["training_config"]["metrics"]
            self.monitor_tab.set_metrics_config(metrics)

    def _on_node_selected(self, node):
        """Обработка выбора узла на графе."""
        if node:
            self.status_bar.showMessage(f"Selected Node: {node.name()}")
        else:
            self.status_bar.showMessage("No node selected")

    def _on_project_loaded(self, project_data: dict):
        """Обработка загрузки проекта."""
        name = project_data.get("metadata", {}).get("name", "Untitled")
        self.setWindowTitle(f"{name} - NeuralNet Designer")
        self._modified = False

    def _on_project_saved(self, path: str):
        """Обработка сохранения проекта."""
        name = self.project_manager.get_project_name()
        self.setWindowTitle(f"{name} - NeuralNet Designer")
        self._modified = False

    def _on_project_changed(self):
        """Обработка изменений в проекте."""
        self._modified = True
        name = self.project_manager.get_project_name()
        self.setWindowTitle(f"{name}* - NeuralNet Designer")
