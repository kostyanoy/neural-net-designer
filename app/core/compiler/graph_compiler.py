from typing import Dict, List

from NodeGraphQt import NodeGraph
from torch import nn

from core.compiler.model_builder import DynamicGraphModel
from core.nodes import ActivationNode
from core.nodes.base_node import MyBaseNode


class GraphCompiler:
    """Преобразует визуальный граф NodeGraphQt узлов в nn.Module."""

    LAYER_FACTORIES = {
        "Activation": lambda node: GraphCompiler._create_activation(node),
        "Dense": lambda node: nn.LazyLinear(
            out_features=node.get_property("units"),
            bias=node.get_property("use_bias"),
        ),
        "Flatten": lambda node: nn.Flatten(),
        "Input": lambda node: None,
        "Merge": lambda node: MergeLayer(node.get_property("mode")),
        "Output": lambda node: None,
        "Split": lambda node: SplitLayer(),
    }

    def __init__(self):
        self._layers: Dict[str, nn.Module] = {}
        self._connections: List[Dict] = []
        self._execution_order: List[str] = []

    def compile(self, graph: NodeGraph):
        """Компиляция графа в nn.Module для обучения."""
        nodes: List[MyBaseNode] = graph.all_nodes()
        self._connections = self._get_all_connections(nodes)
        self._execution_order = self._topological_sort(nodes, self._connections)

        self._layers = {}
        for node_name in self._execution_order:
            node = self._find_node_by_name(nodes, node_name)
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
    def _topological_sort(nodes: List, connections: List) -> List[str]:
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

        assert len(result) == len(
            node_names), f"Обнаружен цикл в графе: количество узлов {len(node_names)} не равно полученному алгоритмом {len(result)}"
        return result

    @staticmethod
    def _find_node_by_name(nodes: List[MyBaseNode], node_name: str):
        """Находит узел по имени"""
        for node in nodes:
            if node.name() == node_name:
                return node
        return None

    @staticmethod
    def _get_all_connections(nodes: List[MyBaseNode]):
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

        connections = GraphCompiler._get_all_connections(nodes)
        try:
            GraphCompiler._topological_sort(nodes, connections)
        except AssertionError as e:
            return {"is_valid": False, "error": "Обнаружен цикл в графе"}

        return {"is_valid": True, "error": ""}

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
