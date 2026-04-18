from app.core.nodes.base_node import MyBaseNode
from app.core.nodes.properties import ComboProperty


class MergeNode(MyBaseNode):
    """Узел слияния нескольких ветвей графа."""
    NODE_NAME = "Merge"
    PROPERTY_SCHEMA = {
        "mode": ComboProperty(
            label="Режим слияния:",
            default="sum",
            options=["sum", "mean"]
        )
    }

    def _init_ports(self):
        """Инициализация портов узла Merge."""
        self.add_input_port("input_0")
        self.add_input_port("input_1")
        self.add_output_port("output")

    def validate_shape(self, input_shapes: list[tuple]) -> tuple[bool, str]:
        if len(input_shapes) != 2:
            return False, f"{self.NODE_NAME}: требуется минимум 2 входа {input_shapes}"

        if len(set(input_shapes)) > 1:
            return False, f"{self.NODE_NAME}: Для sum/mean все входы должны иметь одинаковую размерность {input_shapes}"
        return True, ""

    def transform_shape(self, input_shapes: list[tuple]) -> tuple | None:
        return input_shapes[0] if input_shapes else None
