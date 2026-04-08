from typing import Tuple

import torch
from torch import nn


class SplitLayer(nn.Module):
    """Слой для разветвления графа"""

    def __init__(self):
        super().__init__()
        # TODO сделать динамическим
        self.num_outputs = 2

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        """Выполняет прямое распространение для слоя разветвления."""
        return tuple(x for _ in range(self.num_outputs))
