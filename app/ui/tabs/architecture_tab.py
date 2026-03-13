from NodeGraphQt import NodeGraph
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDockWidget, QLineEdit, QLabel, QListWidget, QAbstractItemView, \
    QListWidgetItem

from core.nodes.dense_node import DenseNode


class ArchitectureTab(QWidget):
    """Вкладка для визуального проектирования архитектуры нейросети."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._register_nodes()

        self.graph.create_node("neural_net.DenseNode")


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
        self.search_input.textChanged.connect(self._filter_blocks)
        layout.addWidget(self.search_input)

        self.block_list = QListWidget()
        self.block_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.block_list.setMovement(QListWidget.Movement.Static)
        self.block_list.setDragEnabled(True)
        self.block_list.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        layout.addWidget(self.block_list)

        self._populate_blocks_list()
        self.block_list.installEventFilter(self)

        dock.setWidget(container)
        return dock

    def _populate_blocks_list(self):
        """Заполнение списка доступных блоков."""
        self.block_list.clear()

        # TODO from config
        blocks = [
            {"name": "Dense", "id": "neural_net.DenseNode", "icon": "🔷"},
        ]

        for block in blocks:
            item = QListWidgetItem(f"{block['icon']} {block['name']}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, block["id"])
            self.block_list.addItem(item)

    def _create_central_area(self):
        """Создание центральной области для canvas."""
        self.graph = NodeGraph()
        graph_widget = self.graph.widget
        graph_widget.setParent(self)
        return graph_widget

    def _create_right_dock(self) -> QDockWidget:
        """Создание правой панели с настройками слоя."""
        dock = QDockWidget("⚙️ Свойства", self)
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

    def _register_nodes(self):
        """Регистрация узлов в NodeGraph."""
        self.graph.register_node(DenseNode)

    def _filter_blocks(self, text):
        """Фильтрация списка блоков по поиску."""
        for i in range(self.block_list.count()):
            item = self.block_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
