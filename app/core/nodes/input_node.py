from app.core.nodes.base_node import MyBaseNode
from app.core.nodes.properties import TextProperty


class InputNode(MyBaseNode):
    """Узел входного слоя нейронной сети."""
    NODE_NAME = 'Input'
    PROPERTY_SCHEMA = {
        "input_shape": TextProperty(
            label="Размеры:",
            default="28, 28",
            placeholder="(размер1, размер2)"
        )
    }

    def _init_ports(self):
        """Инициализация портов узла Input."""
        self.add_output_port("output")

    def transform_shape(self, input_shape: tuple) -> tuple | None:
        """Возвращает размерность выхода Input узла"""
        shape_str = self.get_property("input_shape")
        try:
            shape = tuple(int(x.strip()) for x in shape_str.split(","))
            return shape
        except (ValueError, AttributeError):
            return None

    def validate_shape(self, input_shape: tuple) -> tuple:
        """Проверяет размерность Input"""
        shape_str = self.get_property("input_shape")
        try:
            shape = tuple(int(x.strip()) for x in shape_str.strip("()[] ").split(","))
            return True, ""
        except (ValueError, AttributeError):
            return False, f"{self.NODE_NAME}: Не получается преобразовать строку к формату (dim0, dim1, ...) {shape_str}"
