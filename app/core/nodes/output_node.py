from core.nodes.base_node import MyBaseNode


class OutputNode(MyBaseNode):
    """Узел выходного слоя нейронной сети."""
    NODE_NAME = "Output"

    def _init_ports(self):
        """Инициализация портов узла Output."""
        self.add_input_port("input")