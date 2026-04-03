from core.nodes.base_node import MyBaseNode


class SplitNode(MyBaseNode):
    NODE_NAME = "Split"

    def _init_ports(self):
        self.add_input('input')
        self.add_output('output_0')
        self.add_output('output_1')