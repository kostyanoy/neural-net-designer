from core.nodes.base_node import MyBaseNode
from core.nodes.properties import TextProperty


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
