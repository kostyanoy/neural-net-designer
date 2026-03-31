from core.nodes.base_node import MyBaseNode, PropertyType


class InputNode(MyBaseNode):
    NODE_NAME = 'Input'
    PROPERTY_SCHEMA = {
        "input_shape": {
            "type": PropertyType.TEXT,
            "label": "Размеры:",
            "default": "28, 28",
            "placeholder": "(размер1, размер2)"
        }
    }

    def _init_ports(self):
        self.add_output("output")