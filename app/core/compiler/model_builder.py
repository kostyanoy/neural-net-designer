from typing import Dict, List, Tuple

import torch
from torch import nn

from app.core.compiler.merge_layer import MergeLayer


class DynamicGraphModel(nn.Module):
    """Динамическая модель PyTorch, исполняющая граф узлов."""

    def __init__(self, layers: Dict[str, nn.Module], connections: List[Dict[str, str]], execution_order: List[str]):
        super().__init__()
        self._layers = nn.ModuleDict(layers)
        self._connections = connections
        self._execution_order = execution_order

        self._input_node_name = self._execution_order[0]
        self._output_node_name = self._execution_order[-1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Прямой проход по графу."""
        tensors: Dict[Tuple[str, str], torch.Tensor] = {}  # {(node_name, port_name): tensor}
        tensors[(self._input_node_name, "output")] = x

        for node_name in self._execution_order:
            if node_name not in self._layers:
                continue
            input_tensors = self._get_inputs_for_node(node_name, tensors)
            layer = self._layers[node_name]

            if isinstance(layer, MergeLayer):
                output = layer(input_tensors)
            else:
                output = layer(input_tensors[0])
            if isinstance(output, tuple):
                for i, output_tensor in enumerate(output):
                    port_name = f"output_{i}"
                    tensors[(node_name, port_name)] = output_tensor
            else:
                tensors[(node_name, "output")] = output

        for conn in self._connections:
            if conn["to_node"] == self._output_node_name:
                key = (conn["from_node"], conn["from_port"])
                return tensors[key]

        raise KeyError("Не нашлось выхода модели")

    def _get_inputs_for_node(self, node_name: str, tensors: Dict[Tuple[str, str], torch.Tensor]):
        """Собрать все входные тензоры для узла на основе соединений."""
        keys = []
        for conn in self._connections:
            if conn["to_node"] == node_name:
                from_key = (conn["from_node"], conn["from_port"])
                keys.append((conn["to_port"], from_key))
        keys.sort(key=lambda x: x[0])  # sort by node input ports (input_0, input_1, ...)
        input_tensors = [tensors[key] for _, key in keys]
        return input_tensors

    def get_layer_count(self):
        """Получить количество слоев в модели."""
        return len(self._layers)

    def summary(self):
        """Краткое описание архитектуры модели."""
        lines = [
            "=" * 50,
            "Model Architecture Summary",
            "=" * 50,
            f"Total layers: {self.get_layer_count()}",
            f"Execution order: {len(self._execution_order)} nodes",
            "-" * 50
        ]

        for node_name in self._execution_order:
            if node_name in self._layers:
                layer = self._layers[node_name]
                lines.append(f"{node_name}: {layer.__class__.__name__}")
            else:
                lines.append(f"[{node_name}]")

        lines.append("=" * 50)
        return "\n".join(lines)
