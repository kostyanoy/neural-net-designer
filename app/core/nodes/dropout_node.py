from core.nodes.base_node import MyBaseNode
from core.nodes.properties import FloatProperty


class DropoutNode(MyBaseNode):
    """Узел слоя Dropout для регуляризации нейронной сети."""
    NODE_NAME = "Dropout"
    PROPERTY_SCHEMA = {
        "p": FloatProperty(
            label="Вероятность отключения (p):",
            default=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.05,
        )
    }

    def _init_ports(self):
        """Инициализация портов узла Dropout."""
        self.add_input_port("input")
        self.add_output_port("output")

