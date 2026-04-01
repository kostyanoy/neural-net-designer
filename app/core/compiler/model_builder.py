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

    def forward(self):
        pass

    def _get_input_for_node(self, node_name: str, tensors: Dict[str, torch.Tensor]):
        pass

    def get_layer_count(self):
        return len(self._layers)

    def summary(self):
        pass



