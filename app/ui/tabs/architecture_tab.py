from typing import Optional

from NodeGraphQt import NodeGraph
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDockWidget, QLineEdit, QListWidget, QAbstractItemView, \
    QListWidgetItem, QPushButton, QLabel
from torch import nn

from core.compiler import GraphCompiler
from core.nodes import ActivationNode, FlattenNode, InputNode, OutputNode, MergeNode, SplitNode
from core.nodes.base_node import MyBaseNode
from core.nodes.dense_node import DenseNode
from core.project_manager import ProjectManager
from ui.widgets.draggable_list_widget import DraggableListWidget
from ui.widgets.property_panel import PropertyPanel


class ArchitectureTab(QWidget):
    """Вкладка для визуального проектирования архитектуры нейросети."""
    validation_changed = pyqtSignal(bool)
    proceed_requested = pyqtSignal()

    def __init__(self, parent, project_manager: ProjectManager):
        super().__init__(parent)
        self._init_ui()
        self._register_nodes()
        self._connect_signals()

        self._project_manager = project_manager
        self._graph_compiler = GraphCompiler()
        self._compiled_model = None
        self._is_valid = False

    def _init_ui(self):
        """Инициализация UI элементов вкладки архитектуры."""
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

        self.validate_btn = QPushButton("Валидировать граф")
        self.validate_btn.clicked.connect(self._on_validate_graph)
        layout.addWidget(self.validate_btn)

        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)

        self.next_btn = QPushButton("➡️ Далее: Обучение")
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск слоя...")
        self.search_input.textChanged.connect(self._filter_blocks)
        layout.addWidget(self.search_input)

        self.block_list = DraggableListWidget()
        self.block_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.block_list.setMovement(QListWidget.Movement.Static)
        self.block_list.setDragEnabled(True)
        self.block_list.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        layout.addWidget(self.block_list)

        self._populate_blocks_list()

        dock.setWidget(container)
        return dock

    def _populate_blocks_list(self):
        """Заполнение списка доступных блоков."""
        self.block_list.clear()

        # TODO from config
        blocks = [
            {"name": "Input", "id": "neural_net.InputNode", "icon": "🟢"},
            {"name": "Dense", "id": "neural_net.DenseNode", "icon": "🔷"},
            {"name": "Activation", "id": "neural_net.ActivationNode", "icon": "🟣"},
            {"name": "Flatten", "id": "neural_net.FlattenNode", "icon": "🟠"},
            {"name": "Split", "id": "neural_net.SplitNode", "icon": "🔀"},
            {"name": "Merge", "id": "neural_net.MergeNode", "icon": "🔗"},
            {"name": "Output", "id": "neural_net.OutputNode", "icon": "🔴"},
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

        self.graph_view = self.graph.viewer()
        self.graph_view.setAcceptDrops(True)
        self.graph_view.installEventFilter(self)

        return graph_widget

    def _create_right_dock(self) -> QDockWidget:
        """Создание правой панели с настройками слоя."""
        dock = QDockWidget("⚙️ Свойства", self)
        self.property_panel = PropertyPanel(self)
        self.property_panel.property_changed.connect(self._on_property_changed)
        dock.setWidget(self.property_panel)
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
        self.graph.register_node(ActivationNode)
        self.graph.register_node(DenseNode)
        self.graph.register_node(FlattenNode)
        self.graph.register_node(InputNode)
        self.graph.register_node(MergeNode)
        self.graph.register_node(OutputNode)
        self.graph.register_node(SplitNode)

    def _filter_blocks(self, text):
        """Фильтрация списка блоков по поиску."""
        for i in range(self.block_list.count()):
            item = self.block_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def eventFilter(self, source, event):
        """Перехват событий Drag & Drop."""
        if event.type() == QEvent.DragEnter:
            if event.mimeData().hasFormat(DraggableListWidget.NODE_MIME_TYPE):
                event.acceptProposedAction()
                return True

        if event.type() == QEvent.Drop:
            if event.mimeData().hasFormat(DraggableListWidget.NODE_MIME_TYPE):
                raw_data = event.mimeData().data(DraggableListWidget.NODE_MIME_TYPE)
                node_id = raw_data.data().decode('utf-8')
                scene_pos = self.graph_view.mapToScene(event.pos())
                self.graph.create_node(node_id, pos=(scene_pos.x(), scene_pos.y()))
                self._on_nodes_selected()
                event.acceptProposedAction()
                return True

        return super().eventFilter(source, event)

    def _connect_signals(self):
        """Подключение сигналов для синхронизации свойств"""
        self.graph.node_selection_changed.connect(self._on_nodes_selected)
        self.graph.property_changed.connect(self._on_node_property_changed)

        self.graph.node_created.connect(self._on_graph_changed)
        self.graph.nodes_deleted.connect(self._on_graph_changed)
        self.graph.port_connected.connect(self._on_graph_changed)
        self.graph.port_disconnected.connect(self._on_graph_changed)

    def _on_graph_changed(self):
        """Обработка изменений в графе."""
        self._on_validate_graph()
        self._project_manager.project_changed.emit()

    def _on_validate_graph(self):
        """Проверка графа на корректность"""
        validation_result = self._graph_compiler.validate_graph(self.graph)
        if validation_result["is_valid"]:
            self._is_valid = True
            self.next_btn.setEnabled(True)
            self.validation_label.setText("✅ Граф валиден!")
            self._apply_shapes_to_nodes(validation_result["shapes"])
        else:
            self._is_valid = False
            self.next_btn.setEnabled(False)
            self.validation_label.setText(validation_result["error"])
            self._apply_shapes_to_nodes({})
        self.validation_changed.emit(self._is_valid)
        return validation_result

    def _apply_shapes_to_nodes(self, shapes: dict):
        """Обновляет отображение размерностей на всех узлах графа."""
        connections = self._graph_compiler._get_all_connections(self.graph.all_nodes())

        for node in self.graph.all_nodes():
            node_name = node.name()
            input_shape = None
            output_shape = shapes.get(node_name)

            for conn in connections:
                if conn["to_node"] == node_name:
                    input_shape = shapes.get(conn["from_node"])

            node.update_shape_display(input_shapes=input_shape, output_shape=output_shape)

    def _on_next_clicked(self):
        """Переход на вкладку обучения"""
        if self._is_valid:
            self.proceed_requested.emit()

    def _on_nodes_selected(self):
        """При выборе узла - загрузить его свойства в правую панель"""
        nodes = self.graph.selected_nodes()
        if len(nodes) == 0:
            self.property_panel.set_node(None)
        else:
            self.property_panel.set_node(nodes[0])

    def _on_node_property_changed(self, node: MyBaseNode, prop_name: str, prop_value: object):
        """При изменении свойства"""
        if self.property_panel.current_node == node:
            self.property_panel.update_property_value(prop_name, prop_value)
        self._on_graph_changed()

    def delete_selected_nodes(self):
        """Удаляет выбранные узлы и обновляет валидацию."""
        selected = self.graph.selected_nodes()
        if selected:
            self.graph.delete_nodes(selected)

    def select_all_nodes(self):
        """Выделяет все узлы на канвасе."""
        self.graph.select_all()

    def copy_selected_nodes(self):
        """Копирует выбранные узлы во внутренний буфер NodeGraph."""
        selected = self.graph.selected_nodes()
        if selected:
            self.graph.copy_nodes(selected)

    def paste_nodes(self):
        """Вставляет узлы из буфера. Сдвигает координаты для удобства."""
        self.graph.paste_nodes()

    def _on_property_changed(self, prop_name: str, prop_value: object):
        """Обработка изменения свойства из панели"""
        self._project_manager.project_changed.emit()

    def serialize_graph(self) -> dict:
        """Сериализовать граф NodeGraphQt в формат проекта."""
        data = self.graph.serialize_session()
        return {
            "nodes": data.get("nodes", []),
            "connections": data.get("connections", [])
        }

    def deserialize_graph(self, data: dict):
        """Восстановить граф из данных проекта."""
        try:
            self.graph.deserialize_session(data)
        except Exception as e:
            print(f"Error deserializing graph: {e}")

    def get_model(self) -> Optional[nn.Module]:
        """Получить скомпилированную модель PyTorch."""
        validation_result = self._on_validate_graph()
        if not validation_result["is_valid"]:
            return None
        self._compiled_model = self._graph_compiler.compile(self.graph)
        return self._compiled_model
