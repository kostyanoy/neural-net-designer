from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QSlider

from core.nodes.base_node import MyBaseNode, PropertyType


class PropertyPanel(QWidget):
    """Панель свойств для редактирования параметров выбранного узла"""

    property_changed = pyqtSignal(str, object)  # (prop_name, prop_value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node = None
        self.property_widgets = {}
        self.property_containers = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_label = QLabel("Свойства блока")
        layout.addWidget(self.title_label)

        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout()
        self.properties_container.setLayout(self.properties_layout)
        layout.addWidget(self.properties_container)

        layout.addStretch()

    def set_node(self, node: MyBaseNode | None):
        """Установить текущий узел для редактирования"""
        self.current_node = node
        self._clear_properties()

        if node is None:
            self.title_label.setText("Свойства блока")
            return

        self.title_label.setText(f"Свойства: {node.name()}")
        self._load_properties(node)

    def _clear_properties(self):
        """Очистить все виджеты свойств"""
        self.property_widgets.clear()
        self.property_containers.clear()
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _load_properties(self, node: MyBaseNode):
        """Загрузить свойства узла в панель"""
        schema = node.get_property_schema()
        for prop_name, prop_def in schema.items():
            container, widget = self._create_property_widget(prop_name, prop_def)

            self.property_widgets[prop_name] = widget
            self.property_containers[prop_name] = container
            self.properties_layout.addWidget(container)

            cur_value = node.get_property(prop_name)
            self._set_widget_value(widget, prop_def["type"], cur_value)

    def _create_property_widget(self, prop_name: str, prop_def: dict):
        """Создать UI элемент для свойства"""
        ptype = prop_def["type"]
        label = prop_def["label"]

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        if ptype == PropertyType.INT:
            widget = QSpinBox()
            widget.setRange(prop_def["min"], prop_def["max"])
            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif ptype == PropertyType.FLOAT:
            widget = QDoubleSpinBox()
            widget.setRange(prop_def["min"], prop_def["max"])
            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif ptype == PropertyType.COMBO:
            widget = QComboBox()
            widget.addItems(prop_def["options"])
            widget.currentTextChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif ptype == PropertyType.CHECKBOX:
            widget = QCheckBox()
            widget.stateChanged.connect(lambda v: self._on_property_changed(prop_name, v == 2))
        elif ptype == PropertyType.SLIDER:
            widget = QSlider()
            widget.setOrientation(Qt.Orientation.Horizontal)
            widget.setRange(int(prop_def["min"] * 10), int(prop_def["max"] * 10))
            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v / 10.0))
        else:
            return None, None

        layout.addWidget(widget)
        return container, widget

    def _set_widget_value(self, widget: QWidget, ptype: PropertyType, value):
        """Установить значение в виджет"""
        if ptype == PropertyType.INT:
            widget.setValue(int(value))
        elif ptype == PropertyType.FLOAT:
            widget.setValue(float(value))
        elif ptype == PropertyType.COMBO:
            widget.setCurrentText(value)
        elif ptype == PropertyType.CHECKBOX:
            widget.setChecked(bool(value))
        elif ptype == PropertyType.SLIDER:
            widget.setValue(int(value * 10))

    def _on_property_changed(self, prop_name: str, value):
        """Обработка изменения свойства"""
        if self.current_node:
            self.current_node.set_property(prop_name, value)
            self.property_changed.emit(prop_name, value)

    def update_property_value(self, prop_name, value):
        """Обновить значение виджета при внешнем изменении"""
        if prop_name in self.property_widgets:
            widget = self.property_widgets[prop_name]
            schema = self.current_node.get_property_schema()
            self._set_widget_value(widget, schema[prop_name]["type"], value)
