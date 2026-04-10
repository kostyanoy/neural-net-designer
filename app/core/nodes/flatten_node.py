from core.nodes.base_node import MyBaseNode


class FlattenNode(MyBaseNode):
    """Узел выравнивания тензора"""
    NODE_NAME = "Flatten"

    def _init_ports(self):
        """Инициализация портов узла Flatten."""
        self.add_input_port("input")
        self.add_output_port("output")

    def transform_shape(self, input_shape: tuple) -> tuple:
        if not input_shape:
            return None
        total_features = 1
        for dim in input_shape:
            total_features *= dim
        return (total_features,)