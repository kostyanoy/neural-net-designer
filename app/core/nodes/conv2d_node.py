from app.core.nodes.base_node import MyBaseNode
from app.core.nodes.properties import IntProperty, CheckboxProperty


class Conv2DNode(MyBaseNode):
    """Узел двумерной свёртки (Conv2D)."""
    NODE_NAME = "Conv2D"
    PROPERTY_SCHEMA = {
        "out_channels": IntProperty(
            label="Выходных каналов:",
            default=32,
            min_value=1,
            max_value=10000,
        ),
        "kernel_size": IntProperty(
            label="Размер ядра:",
            default=3,
            min_value=1,
            max_value=50,
        ),
        "stride": IntProperty(
            label="Шаг:",
            default=1,
            min_value=1,
            max_value=50,
        ),
        "padding": IntProperty(
            label="Padding:",
            default=0,
            min_value=0,
            max_value=50,
        ),
        "bias": CheckboxProperty(
            label="Bias:",
            default=True,
        )
    }

    def _init_ports(self):
        self.add_input_port("input")
        self.add_output_port("output")

    def validate_shape(self, input_shape: tuple) -> tuple[bool, str]:
        if len(input_shape) != 3:
            return False, f"{self.NODE_NAME}: Ожидается минимум 3D (C, H, W), получено {len(input_shape)}D {input_shape}"
        return True, ""

    def transform_shape(self, input_shape: tuple) -> tuple | None:
        if not input_shape or len(input_shape) != 3:
            return None
        in_channels, h_in, w_in = input_shape
        out_channels = self.get_property("out_channels")
        k = self.get_property("kernel_size")
        s = self.get_property("stride")
        p = self.get_property("padding")

        h_out = (h_in + 2 * p - k) // s + 1
        w_out = (w_in + 2 * p - k) // s + 1

        return out_channels, h_out, w_out
