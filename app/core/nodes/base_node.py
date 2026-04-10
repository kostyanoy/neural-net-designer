from NodeGraphQt import BaseNode
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsTextItem

from core.nodes.properties import Property


class MyBaseNode(BaseNode):
    """Базовый класс для пользовательских узлов в графе нейронной сети."""
    __identifier__ = 'neural_net'
    NODE_NAME = 'Base'

    # Переопределяется в наследниках
    PROPERTY_SCHEMA: dict[str, Property] = {}

    def __init__(self):
        super().__init__()
        self._dim_label = None
        self.node_type = self.NODE_NAME

        self._init_ports()
        self._init_properties()
        self._init_shape_labels()

    def _init_properties(self):
        """Инициализирует свойства БЕЗ UI виджетов в узле"""
        for prop_name, prop_def in self.PROPERTY_SCHEMA.items():
            default_value = prop_def.default
            self.create_property(prop_name, default_value)

    def _init_ports(self):
        """Инициализация портов узла"""
        pass

    def _init_shape_labels(self):
        """Создаёт пустые текстовые метки для узла."""
        self._dim_label = QGraphicsTextItem("(123,) -> (12,)", self.view)
        self._dim_label.setDefaultTextColor(QColor(255, 255, 255))
        px, py = self.view.x(), self.view.y()
        self._dim_label.setPos(px + 30, py - 20)

    def update_shape_display(self, input_shapes: dict = None, output_shape: tuple = None):
        """Обновляет текст и позиции меток размерностей."""
        if input_shapes is None and output_shape is None:
            self._dim_label.setPlainText("")
        elif input_shapes is None:
            self._dim_label.setPlainText(f"{output_shape}")
        elif output_shape is None:
            self._dim_label.setPlainText(f"{input_shapes}")
        else:
            self._dim_label.setPlainText(f"{input_shapes} -> {output_shape}")

        node_rect = self.view.boundingRect()
        text_rect = self._dim_label.boundingRect()

        x = (node_rect.width() - text_rect.width()) / 2
        y = -text_rect.height()
        self._dim_label.setPos(x, y)


    def add_input_port(self, name):
        """Создание входного порта"""
        self.add_input(name, multi_input=False)

    def add_output_port(self, name):
        """Создание выходного порта"""
        self.add_output(name, multi_output=False)

    def transform_shape(self, input_shape: tuple) -> tuple | None:
        """Преобразует входную размерность в выходную. Возвращает None если не может обработать."""
        if input_shape is None:
            return None
        return input_shape

    def validate_shape(self, input_shape: tuple) -> tuple[bool, str]:
        """Проверяет совместимость входной размерности. Возвращает (is_valid, error_message)"""
        if input_shape is None:
            return False, f"{self.NODE_NAME}: Некорректная входная размерность для узла {input_shape}"
        return True, ""

    @classmethod
    def get_property_schema(cls):
        """Возвращает схему свойств текущего узла."""
        return cls.PROPERTY_SCHEMA

    def get_property_value(self, prop_name):
        """Получает текущее значение указанного свойства."""
        return self.get_property(prop_name)

    def set_property_value(self, prop_name, value):
        """Устанавливает новое значение для указанного свойства."""
        self.set_property(prop_name, value)
