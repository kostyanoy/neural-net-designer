from core.nodes.base_node import MyBaseNode
from core.nodes.properties import ComboProperty, IntProperty


class PoolingNode(MyBaseNode):
    """Узел слоя пулинга (MaxPool2D / AvgPool2D)."""
    NODE_NAME = "Pooling"
    PROPERTY_SCHEMA = {
        "pool_type": ComboProperty(
            label="Тип пулинга:",
            default="max",
            options=["max", "avg"],
        ),
        "kernel_size": IntProperty(
            label="Размер ядра:",
            default=2,
            min_value=1,
            max_value=10,
        ),
        "stride": IntProperty(
            label="Шаг:",
            default=2,
            min_value=1,
            max_value=10,
        ),
        "padding": IntProperty(
            label="Padding:",
            default=0,
            min_value=0,
            max_value=10,
        )
    }

    def _init_ports(self):
        """Инициализация портов узла пулинга."""
        self.add_input_port("input")
        self.add_output_port("output")

    def validate_shape(self, input_shape: tuple) -> tuple[bool, str]:
        if input_shape is None:
            return False, f"{self.NODE_NAME}: Некорректная входная размерность для узла {input_shape}"
        if len(input_shape) != 3:
            return False, f"{self.NODE_NAME}: ожидается 3D тензор (C, H, W), получено {len(input_shape)}D {input_shape}"
        return True, ""

    def transform_shape(self, input_shape: tuple) -> tuple | None:
        if input_shape is None or len(input_shape) != 3:
            return None
        in_channels, h_in, w_in = input_shape
        k = self.get_property("kernel_size")
        s = self.get_property("stride")
        p = self.get_property("padding")

        h_out = (h_in + 2 * p - k) // s + 1
        w_out = (w_in + 2 * p - k) // s + 1

        return in_channels, h_out, w_out
