from typing import Dict, List

import torch
from torch import nn


class DynamicGraphModel(nn.Module):
    """Динамическая модель PyTorch, исполняющая граф узлов."""
    def __init__(self, layers: Dict[str, nn.Module], connections: List[Dict], execution_order: List[str]):
        super().__init__()
        self._layers = layers
        self._connections = connections
        self._execution_order = execution_order

        self._input_node_name = self._execution_order[0]
        self._output_node_name = self._execution_order[-1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Прямой проход по графу."""
        tensors: Dict[str, torch.Tensor] = {}
        tensors[self._input_node_name] = x

        for node_name in self._execution_order:
            if node_name not in self._layers:
                continue
            input_tensor = self._get_input_for_node(node_name, tensors)
            layer = self._layers[node_name]
            output_tensor = layer(input_tensor)
            tensors[node_name] = output_tensor

        return tensors[self._output_node_name]


    def _get_input_for_node(self, node_name: str, tensors: Dict[str, torch.Tensor]):
        pass

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



