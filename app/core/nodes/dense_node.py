from app.core.nodes.base_node import MyBaseNode
from app.core.nodes.properties import IntProperty, CheckboxProperty


class DenseNode(MyBaseNode):
    """Узел полносвязного слоя (Dense/Linear)."""
    NODE_NAME = 'Dense'
    PROPERTY_SCHEMA = {
        "units": IntProperty(
            label="Нейроны:",
            default=64,
            min_value=1,
            max_value=10000
        ),
        "use_bias": CheckboxProperty(
            label="Bias:",
            default=True
        )
    }

    def _init_ports(self):
        """Инициализация портов узла Dense."""
        self.add_input_port('input')
        self.add_output_port('output')

    def validate_shape(self, input_shape: tuple) -> tuple[bool, str]:
        if len(input_shape) > 1:
            return False, f"{self.NODE_NAME}: требуется 1D вход, получено {len(input_shape)}D {input_shape}"
        return True, ""

    def transform_shape(self, input_shape: tuple) -> tuple:
        units = self.get_property("units")
        return (units,)
