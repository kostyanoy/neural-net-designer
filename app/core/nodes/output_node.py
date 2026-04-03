from core.nodes.base_node import MyBaseNode


class OutputNode(MyBaseNode):
    NODE_NAME = "Output"

    def _init_ports(self):
        self.add_input_port("input")