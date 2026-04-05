from core.nodes.base_node import MyBaseNode
from core.nodes.properties import ComboProperty


class MergeNode(MyBaseNode):
    """Узел слияния нескольких ветвей графа."""
    NODE_NAME = "Merge"
    PROPERTY_SCHEMA = {
        "mode": ComboProperty(
            label="Режим слияния:",
            default="concat",
            options=["concat", "sum", "mean"]
        )
    }

    def _init_ports(self):
        """Инициализация портов узла Merge."""
        self.add_input_port("input_0")
        self.add_input_port("input_1")
        self.add_output_port("output")