from typing import Dict, List

from NodeGraphQt import NodeGraph
from torch import nn

from app.core.compiler.merge_layer import MergeLayer
from app.core.compiler.model_builder import DynamicGraphModel
from app.core.compiler.split_layer import SplitLayer
from app.core.nodes import ActivationNode, PoolingNode
from app.core.nodes.base_node import MyBaseNode


class GraphCompiler:
    """Преобразует визуальный граф NodeGraphQt узлов в nn.Module."""

    LAYER_FACTORIES = {
        "Activation": lambda node: GraphCompiler._create_activation(node),
        "Conv2D": lambda node: nn.LazyConv2d(
            out_channels=node.get_property("out_channels"),
            kernel_size=node.get_property("kernel_size"),
            stride=node.get_property("stride"),
            padding=node.get_property("padding"),
            bias=node.get_property("bias"),
        ),
        "Dense": lambda node: nn.LazyLinear(
            out_features=node.get_property("units"),
            bias=node.get_property("use_bias"),
        ),
        "Dropout": lambda node: nn.Dropout(p=node.get_property("p")),
        "Flatten": lambda node: nn.Flatten(),
        "Input": lambda node: None,
        "Merge": lambda node: MergeLayer(node.get_property("mode")),
        "Output": lambda node: None,
        "Pooling": lambda node: GraphCompiler._create_pooling(node),
        "Split": lambda node: SplitLayer(),
    }

    def __init__(self):
        self._layers: Dict[str, nn.Module] = {}
        self._connections: List[Dict] = []
        self._execution_order: List[str] = []

    def compile(self, graph: NodeGraph):
        """Компиляция графа в nn.Module для обучения."""
        nodes: List[MyBaseNode] = graph.all_nodes()
        self._connections = self.get_all_connections(nodes)
        self._execution_order = self.topological_sort(nodes, self._connections)

        self._layers = {}
        for node_name in self._execution_order:
            node = self.find_node_by_name(nodes, node_name)
            if node:
                layer = self._create_layer(node)
                if layer is not None:
                    self._layers[node_name] = layer

        model = DynamicGraphModel(
            layers=self._layers,
            connections=self._connections,
            execution_order=self._execution_order
        )
        return model

    def _create_layer(self, node: MyBaseNode):
        """Создание PyTorch слоя на основе типа узла."""
        node_type = node.node_type
        factory = self.LAYER_FACTORIES[node_type]

        if factory is None:
            print(f"Неизвестный узел: {node_type}. Используем Identity")
            return nn.Identity()
        return factory(node)

    @staticmethod
    def _propagate_shapes(graph: NodeGraph) -> tuple[bool, str, dict]:
        """Распространяет размерности через граф"""
        nodes = graph.all_nodes()
        connections = GraphCompiler.get_all_connections(nodes)
        execution_order = GraphCompiler.topological_sort(nodes, connections)

        shapes = {}
        for node_name in execution_order:
            node = GraphCompiler.find_node_by_name(nodes, node_name)
            input_shapes = GraphCompiler._get_input_shapes_for_node(node_name, connections, shapes)
            if len(input_shapes) == 1:
                input_shapes = input_shapes[0]

            is_valid, error_msg = node.validate_shape(input_shapes)
            if not is_valid:
                return False, error_msg, {}

            output_shape = node.transform_shape(input_shapes)
            shapes[node_name] = output_shape

        return True, "", shapes

    @staticmethod
    def _get_input_shapes_for_node(node_name: str, connections: List[Dict], shapes: Dict) -> List[tuple]:
        """Получает размерности всех входов узла"""
        input_shapes = []
        for conn in connections:
            if conn["to_node"] == node_name:
                from_shape = shapes.get(conn["from_node"])
                input_shapes.append(from_shape)
        return input_shapes

    @staticmethod
    def topological_sort(nodes: List, connections: List) -> List[str]:
        """Сортировка узлов в порядке выполнения (от Input к Output) по алгоритму Кана"""
        node_names = [node.name() for node in nodes]
        in_degree = {node_name: 0 for node_name in node_names}
        adjacency = {node_name: [] for node_name in node_names}

        for conn in connections:
            from_node = conn["from_node"]
            to_node = conn["to_node"]

            adjacency[from_node].append(to_node)
            in_degree[to_node] += 1

        result = []
        queue = [node_name for node_name in node_names if in_degree[node_name] == 0]
        while queue:
            node_name = queue.pop(0)
            result.append(node_name)
            for neighbor in adjacency[node_name]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(node_names):
            raise ValueError(
                f"Обнаружен цикл в графе: "
                f"количество узлов {len(node_names)} не равно полученному алгоритмом {len(result)}"
            )
        return result

    @staticmethod
    def find_node_by_name(nodes: List[MyBaseNode], node_name: str):
        """Находит узел по имени"""
        for node in nodes:
            if node.name() == node_name:
                return node
        return None

    @staticmethod
    def get_all_connections(nodes: List[MyBaseNode]):
        """Собирает все соединения в графе"""
        connections = []
        for node in nodes:
            for input_port in node.input_ports():
                for connected_port in input_port.connected_ports():
                    connections.append({
                        'from_node': connected_port.node().name(),
                        'from_port': connected_port.name(),
                        'to_node': node.name(),
                        'to_port': input_port.name()
                    })
        connections.sort(key=lambda x: (x["from_port"], x["to_port"]))
        return connections

    @staticmethod
    def validate_graph(graph: NodeGraph):
        """Проверяет граф на корректность"""
        nodes: List[MyBaseNode] = graph.all_nodes()

        if len(nodes) == 0:
            return {"is_valid": False, "error": "Граф не содержит узлов"}

        input_nodes = [n for n in nodes if n.node_type == "Input"]
        output_nodes = [n for n in nodes if n.node_type == "Output"]

        if len(input_nodes) == 0:
            return {"is_valid": False, "error": "Нет входного слоя (Input)"}
        elif len(input_nodes) > 1:
            return {"is_valid": False, "error": f"Слишком много входных слоёв: {len(input_nodes)} (должен быть 1)"}

        if len(output_nodes) == 0:
            return {"is_valid": False, "error": "Нет выходного слоя (Output)"}
        elif len(output_nodes) > 1:
            return {"is_valid": False, "error": f"Слишком много выходных слоёв: {len(output_nodes)} (должен быть 1)"}

        connectivity_result = GraphCompiler._check_connectivity(nodes)
        if not connectivity_result["is_connected"]:
            return {"is_valid": False,
                    "error": f"Граф несвязный: {connectivity_result['unconnected_nodes']} узлов изолированы"}

        port_result = GraphCompiler._check_unused_ports(nodes)
        if port_result["unused_inputs"]:
            return {"is_valid": False,
                    "error": f"Не подключены входные порты: {', '.join(port_result['unused_inputs'])}"}
        if port_result["unused_outputs"]:
            return {"is_valid": False,
                    "error": f"Не подключены выходные порты: {', '.join(port_result['unused_outputs'])}"}

        connections = GraphCompiler.get_all_connections(nodes)
        try:
            GraphCompiler.topological_sort(nodes, connections)
        except ValueError as e:
            return {"is_valid": False, "error": "Обнаружен цикл в графе"}

        is_valid, error_msg, shapes = GraphCompiler._propagate_shapes(graph)
        if not is_valid:
            return {"is_valid": False, "error": error_msg}

        return {"is_valid": True, "error": "", "shapes": shapes}

    @staticmethod
    def _check_connectivity(nodes: List[MyBaseNode]) -> Dict:
        """Проверяет, что все узлы принадлежат одному связному графу с помощью BFS"""
        if len(nodes) <= 1:
            return {"is_connected": True, "unconnected_nodes": 0}

        adjacency = {node.name(): set() for node in nodes}
        for node in nodes:
            for input_port in node.input_ports():
                for connected_port in input_port.connected_ports():
                    from_node = connected_port.node().name()
                    to_node = node.name()
                    adjacency[from_node].add(to_node)
                    adjacency[to_node].add(from_node)

        start_node = nodes[0].name()
        visited = {start_node}
        queue = [start_node]
        while queue:
            current_node = queue.pop(0)
            for neighbor in adjacency[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        unconnected_nodes = len(nodes) - len(visited)
        return {"is_connected": unconnected_nodes == 0, "unconnected_nodes": unconnected_nodes}

    @staticmethod
    def _check_unused_ports(nodes: List[MyBaseNode]) -> Dict:
        """Проверяет наличие неподключённых портов"""
        unused_inputs = []
        unused_outputs = []

        for node in nodes:
            for input_port in node.input_ports():
                if not input_port.connected_ports():
                    unused_inputs.append(f"{node.name()}.{input_port.name()}")
            for output_port in node.output_ports():
                if not output_port.connected_ports():
                    unused_outputs.append(f"{node.name()}.{output_port.name()}")

        return {"unused_inputs": unused_inputs, "unused_outputs": unused_outputs}

    @classmethod
    def _create_activation(cls, node: ActivationNode):
        """Фабрика функций активации."""
        func_name: str = node.get_property("function")
        activations = {
            "relu": nn.ReLU(),
            "sigmoid": nn.Sigmoid(),
            "tanh": nn.Tanh(),
            "softmax": nn.Softmax(dim=1),
        }
        return activations[func_name]

    @classmethod
    def _create_pooling(cls, node: PoolingNode):
        """Фабрика слоёв пулинга"""
        pool_type = node.get_property("pool_type")
        if pool_type == "avg":
            return nn.AvgPool2d(
                kernel_size=node.get_property("kernel_size"),
                stride=node.get_property("stride"),
                padding=node.get_property("padding"),
            )
        elif pool_type == "max":
            return nn.MaxPool2d(
                kernel_size=node.get_property("kernel_size"),
                stride=node.get_property("stride"),
                padding=node.get_property("padding"),
            )
        else:
            raise ValueError(f"Неизвестный вид пулинга: {pool_type}")
