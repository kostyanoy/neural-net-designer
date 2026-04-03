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

    def _topological_sort(self, nodes: List, connections: List) -> List[str]:
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

    def _create_layer(self, node: MyBaseNode):
        """Создание PyTorch слоя на основе типа узла."""
        node_type = node.node_type
        factory = self.LAYER_FACTORIES[node_type]

        if factory is None:
            print(f"Неизвестный узел: {node_type}. Используем Identity")
            return nn.Identity()
        return factory(node)

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
        node_types = [node.node_type for node in nodes]

        if len(nodes) == 0:
            return {"is_valid": False, "error": "Граф не содержит узлов"}

        if "Input" not in node_types:
            return {"is_valid": False, "error": "Нет входного слоя"}
        if "Output" not in node_types:
            return {"is_valid": False, "error": "Нет выходного слоя"}

        return {"is_valid": True, "error": ""}

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
