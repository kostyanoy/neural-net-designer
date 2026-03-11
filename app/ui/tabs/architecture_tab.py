from NodeGraphQt import NodeGraph
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDockWidget, QLineEdit, QLabel


class ArchitectureTab(QWidget):
    """Вкладка для визуального проектирования архитектуры нейросети."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.left_dock = self._create_left_dock()
        self.central_widget = self._create_central_area()
        self.right_dock = self._create_right_dock()

        self._configure_docks()

        layout.addWidget(self.central_widget)

    def _create_left_dock(self) -> QDockWidget:
        """Создание левой панели с палитрой блоков."""
        dock = QDockWidget("🧩 Блоки", self)

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Поле поиска
        # TODO
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск слоя...")
        layout.addWidget(self.search_input)

        # Заглушка для списка блоков
        # TODO
        placeholder = QLabel("Список блоков\n(будет позже)")
        placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(placeholder)

        dock.setWidget(container)
        return dock

    def _create_central_area(self):
        """Создание центральной области для canvas."""
        self.graph = NodeGraph()
        graph_widget = self.graph.widget
        graph_widget.setParent(self)
        self.graph.set_grid_mode(True)

        return graph_widget

    def _create_right_dock(self) -> QDockWidget:
        """Создание правой панели с настройками слоя."""
        dock = QDockWidget("⚙️ Свойства", self)

        # Виджет содержимого
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Заглушка для настроек
        # TODO
        placeholder = QLabel("Параметры слоя\n(выберите блок)")
        placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(placeholder)

        dock.setWidget(container)
        return dock

    def _configure_docks(self):
        """Настройка поведения док-панелей."""
        # Разрешаем сворачивание и перемещение
        for dock in [self.left_dock, self.right_dock]:
            dock.setFeatures(
                QDockWidget.DockWidgetClosable |
                QDockWidget.DockWidgetMovable
            )
            dock.setAllowedAreas(
                QtCore.Qt.DockWidgetArea.LeftDockWidgetArea |
                QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            )
