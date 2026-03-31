from core.nodes.base_node import MyBaseNode, PropertyType


class ActivationNode(MyBaseNode):
    NODE_NAME = "Activation"
    PROPERTY_SCHEMA = {
        "function": {
            "type": PropertyType.COMBO,
            "label": "Функция активации:",
            "default": "relu",
            "options": ["relu", "sigmoid", "tanh", "softmax"]
        }
    }

    def _init_ports(self):
        self.add_input("input")
        self.add_output("output")