from core.nodes.base_node import MyBaseNode


class FlattenNode(MyBaseNode):
    """Узел выравнивания тензора"""
    NODE_NAME = "Flatten"

    def _init_ports(self):
        """Инициализация портов узла Flatten."""
        self.add_input_port("input")
        self.add_output_port("output")