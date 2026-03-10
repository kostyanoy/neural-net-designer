from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QDockWidget, QLineEdit


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
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(placeholder)

        dock.setWidget(container)
        return dock

    def _create_central_area(self) -> QWidget:
        """Создание центральной области для canvas."""
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Заглушка для будущего canvas
        # TODO
        placeholder = QLabel("🎨 Canvas для архитектуры\n(перетаскивание блоков)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #666; background-color: #2b2b2b; min-height: 400px;")
        layout.addWidget(placeholder)

        return container

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
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(placeholder)

        dock.setWidget(container)
        return dock

    def _configure_docks(self):
        """Настройка поведения док-панелей."""
        # Разрешаем сворачивание и перемещение
        for dock in [self.left_dock, self.right_dock]:
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetClosable |
                QDockWidget.DockWidgetFeature.DockWidgetMovable
            )
            dock.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea |
                Qt.DockWidgetArea.RightDockWidgetArea
            )