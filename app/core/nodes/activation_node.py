from core.nodes.base_node import MyBaseNode
from core.nodes.properties import ComboProperty


class ActivationNode(MyBaseNode):
    """Узел функции активации нейронной сети."""
    NODE_NAME = "Activation"
    PROPERTY_SCHEMA = {
        "function": ComboProperty(
            label="Функция активации:",
            default="relu",
            options=["relu", "sigmoid", "tanh", "softmax"],
        )
    }

    def _init_ports(self):
        """Инициализация портов узла активации."""
        self.add_input_port("input")
        self.add_output_port("output")
