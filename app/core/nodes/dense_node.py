from core.nodes.base_node import MyBaseNode, PropertyType


class DenseNode(MyBaseNode):
    NODE_NAME = 'Dense'
    PROPERTY_SCHEMA = {
        "units": {
            "type": PropertyType.INT,
            "label": "Нейроны:",
            "default": 64,
            "min": 1,
            "max": 10000
        },
        "use_bias": {
            "type": PropertyType.CHECKBOX,
            "label": "Bias:",
            "default": True
        },
        "dropout": {
            "type": PropertyType.SLIDER,
            "label": "Dropout:",
            "default": 0.0,
            "min": 0.0,
            "max": 0.9,
            "step": 0.1,
        }
    }

    def _init_ports(self):
        self.add_input('input')
        self.add_output('output')
