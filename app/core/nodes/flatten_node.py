from core.nodes.base_node import MyBaseNode


class FlattenNode(MyBaseNode):
    NODE_NAME = "Flatten"

    def _init_ports(self):
        self.add_input_port("input")
        self.add_output_port("output")