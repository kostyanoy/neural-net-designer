from typing import List

import torch
from torch import nn


class MergeLayer(nn.Module):
    """Слой для слияния ветвей"""

    def __init__(self, mode: str = "concat"):
        super().__init__()
        self.mode = mode

    def forward(self, inputs: List[torch.Tensor]) -> torch.Tensor:
        """Выполняет слияние входных тензоров"""
        if self.mode == "concat":
            return torch.cat(inputs, dim=1)
        elif self.mode == "sum":
            return sum(inputs)
        elif self.mode == "mean":
            return sum(inputs) / len(inputs)
        else:
            raise NotImplementedError(f"{self.mode} is not implemented")
