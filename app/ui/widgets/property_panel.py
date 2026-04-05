from typing import cast

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QSlider, \
    QHBoxLayout, QLineEdit

from core.nodes.base_node import MyBaseNode
from core.nodes.properties import IntProperty, FloatProperty, TextProperty, ComboProperty, \
    CheckboxProperty, SliderProperty, Property


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
        """Инициализация UI элементов панели свойств."""
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
            self._set_widget_value(widget, prop_name, prop_def, cur_value)

    def _create_property_widget(self, prop_name: str, prop_def: Property):
        """Создать UI элемент для свойства"""
        label = prop_def.label

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        if isinstance(prop_def, IntProperty):
            widget = QSpinBox()
            widget.setRange(prop_def.min_value, prop_def.max_value)
            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif isinstance(prop_def, FloatProperty):
            widget = QDoubleSpinBox()
            widget.setRange(prop_def.min_value, prop_def.max_value)
            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif isinstance(prop_def, TextProperty):
            widget = QLineEdit()
            widget.setPlaceholderText(prop_def.placeholder)
            widget.textChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif isinstance(prop_def, ComboProperty):
            widget = QComboBox()
            widget.addItems(prop_def.options)
            widget.currentTextChanged.connect(lambda v: self._on_property_changed(prop_name, v))
        elif isinstance(prop_def, CheckboxProperty):
            widget = QCheckBox()
            widget.stateChanged.connect(lambda v: self._on_property_changed(prop_name, v == 2))
        elif type(prop_def) == SliderProperty:
            _min = prop_def.min_value
            _max = prop_def.max_value
            _step = prop_def.step

            widget = QSlider()
            widget.setOrientation(Qt.Orientation.Horizontal)
            widget.setRange(int(_min / _step), int(_max / _step))

            values_layout = QHBoxLayout()
            min_label = QLabel(f"{_min}")
            min_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            value_label = QLabel(f"{prop_def.default}")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            max_label = QLabel(f"{_max}")
            max_label.setAlignment(Qt.AlignmentFlag.AlignRight)

            slider_container = QWidget()
            values_layout.addWidget(min_label)
            values_layout.addWidget(value_label)
            values_layout.addWidget(max_label)
            slider_container.setLayout(values_layout)
            layout.addWidget(slider_container)

            widget.valueChanged.connect(lambda v: self._on_property_changed(prop_name, v * _step))
            self.property_containers[f"{prop_name}_value"] = value_label

        else:
            return None, None


        layout.addWidget(widget)
        return container, widget


    def _set_widget_value(self, widget: QWidget, prop_name, prop_def: Property, value):
        """Установить значение в виджет"""
        if isinstance(prop_def, IntProperty):
            widget.setValue(int(value))
        elif isinstance(prop_def, FloatProperty):
            widget.setValue(float(value))
        elif isinstance(prop_def, TextProperty):
            widget.setText(value)
        elif isinstance(prop_def, ComboProperty):
            widget.setCurrentText(value)
        elif isinstance(prop_def, CheckboxProperty):
            widget.setChecked(bool(value))
        elif isinstance(prop_def, SliderProperty):
            widget.setValue(int(value / prop_def["step"]))
            self.property_containers[f"{prop_name}_value"].setText(str(round(value, 4)))


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
            self._set_widget_value(widget, prop_name, schema[prop_name], value)
