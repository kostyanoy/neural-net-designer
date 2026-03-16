from enum import Enum

from NodeGraphQt import BaseNode


class PropertyType(Enum):
    """Перечисление поддерживаемых типов данных для свойств узлов."""
    INT = "int"
    FLOAT = "float"
    # TEXT = "text"
    COMBO = "combo"
    CHECKBOX = "checkbox"
    SLIDER = "slider"


class MyBaseNode(BaseNode):
    """Базовый класс для пользовательских узлов в графе нейронной сети."""
    __identifier__ = 'neural_net'

    # Переопределяется в наследниках
    PROPERTY_SCHEMA = {}

    def __init__(self):
        super().__init__()
        self._init_ports()
        self._init_properties()

    def _init_properties(self):
        """Инициализирует свойства БЕЗ UI виджетов в узле"""
        for prop_name, prop_def in self.PROPERTY_SCHEMA.items():
            default_value = prop_def["default"]
            self.create_property(prop_name, default_value)

    def _init_ports(self):
        """Инициализация портов узла"""
        pass

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
