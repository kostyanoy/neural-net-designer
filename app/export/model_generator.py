import re
from typing import List, Tuple, Dict

import black
from NodeGraphQt import NodeGraph
from jinja2 import FileSystemLoader, Environment

from config import TEMPLATES_DIR
from core.compiler import GraphCompiler
from core.nodes.base_node import MyBaseNode


class ModelCodeGenerator:
    """Генерирует статический Python-код для модели на основе визуального графа."""

    def __init__(self, graph: NodeGraph):
        self._graph = graph
        self._compiler = GraphCompiler()
        self._nodes = graph.all_nodes()
        self._connections = self._compiler.get_all_connections(self._nodes)
        self._execution_order = self._compiler.topological_sort(self._nodes, self._connections)

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Преобразует произвольное имя узла в валидный Python-идентификатор."""
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip())
        if not clean or clean[0].isdigit():
            clean = f"layer_{clean}"
        return clean.lower()

    @staticmethod
    def _node_to_pytorch(node: MyBaseNode) -> str:
        """Генерирует строку инициализации PyTorch-слоя."""
        t = node.node_type
        if t == "Conv2D":
            return (f"nn.LazyConv2d(out_channels={node.get_property('out_channels')}, "
                    f"kernel_size={node.get_property('kernel_size')}, "
                    f"stride={node.get_property('stride')}, "
                    f"padding={node.get_property('padding')}, "
                    f"bias={node.get_property('bias')})")
        elif t == "Dense":
            return f"nn.LazyLinear(out_features={node.get_property('units')}, bias={node.get_property('use_bias')})"
        elif t == "Dropout":
            return f"nn.Dropout(p={node.get_property('p')})"
        elif t == "Flatten":
            return "nn.Flatten()"
        elif t == "Pooling":
            pt = node.get_property("pool_type")
            k, s, p = node.get_property("kernel_size"), node.get_property("stride"), node.get_property("padding")
            cls = "nn.AvgPool2d" if pt == "avg" else "nn.MaxPool2d"
            return f"{cls}(kernel_size={k}, stride={s}, padding={p})"
        elif t == "Activation":
            fn = node.get_property("function")
            return "nn.Softmax(dim=1)" if fn == "softmax" else f"nn.{fn.capitalize()}()"
        elif t == "Merge":
            return f"MergeLayer(mode='{node.get_property('mode')}')"
        elif t == "Split":
            return f"SplitLayer(num_outputs={len(node.output_ports())})"
        return None

    def _build_layer_definitions(self, name_map: Dict[str, str]) -> List[Tuple[str, str]]:
        """Формирует список определений слоёв для блока __init__."""
        layers = []
        for node_name in self._execution_order:
            node = self._compiler.find_node_by_name(self._nodes, node_name)
            if not node or node.node_type in ("Input", "Output"):
                continue
            layer_def = self._node_to_pytorch(node)
            if layer_def:
                layers.append((name_map[node_name], layer_def))
        return layers

    def _build_forward_statements(self, name_map: Dict[str, str]) -> Tuple[List, bool]:
        """Генерирует последовательность вызовов для метода forward."""
        forward_stmts = []
        tensor_vars = {}
        has_custom = False
        var_counter = 1

        input_node = self._compiler.find_node_by_name(self._nodes, "Input")
        tensor_vars[f"{input_node.name()}:output"] = "x"
        for node_name in self._execution_order:
            node = self._compiler.find_node_by_name(self._nodes, node_name)
            if not node or node.node_type == "Input":
                continue

            input_vars = []
            for conn in self._connections:
                if conn["to_node"] == node_name:
                    key = f"{conn['from_node']}:{conn['from_port']}"
                    var = tensor_vars.get(key)
                    if var:
                        input_vars.append(var)

            if node.node_type == "Output":
                if input_vars:
                    forward_stmts.append(f"return {input_vars[0]}")
                continue

            py_name = name_map[node_name]
            out_var = f"x_{var_counter}"
            var_counter += 1
            src_tensor = input_vars[0] if input_vars else "x"

            if node.node_type == "Split":
                num_out = len(node.output_ports())
                vars_list = [f"{out_var}_{i}" for i in range(num_out)]
                stmt = f"{', '.join(vars_list)} = self.{py_name}({src_tensor})"
                for i, port in enumerate(node.output_ports()):
                    tensor_vars[f"{node_name}:{port.name()}"] = vars_list[i]
                has_custom = True
            elif node.node_type == "Merge":
                stmt = f"{out_var} = self.{py_name}([{', '.join(input_vars)}])"
                tensor_vars[f"{node_name}:output"] = out_var
                has_custom = True
            else:
                stmt = f"{out_var} = self.{py_name}({src_tensor})"
                tensor_vars[f"{node_name}:output"] = out_var
            forward_stmts.append(stmt)

        if not forward_stmts:
            forward_stmts.append("return x")

        return forward_stmts, has_custom

    def generate(self) -> str:
        """Основной метод-оркестратор генерации кода модели."""
        if not self._graph.all_nodes():
            raise ValueError("Граф пуст")

        name_map = {node.name(): self._sanitize_name(node.name()) for node in self._nodes}
        layers = self._build_layer_definitions(name_map)
        forward_stmts, has_custom = self._build_forward_statements(name_map)

        context = {
            "layers": layers,
            "forward_statements": forward_stmts,
            "has_custom_layers": has_custom
        }

        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("model.jinja2")
        raw_code = template.render(**context)

        return black.format_str(raw_code, mode=black.Mode())
