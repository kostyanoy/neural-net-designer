from torch import nn


class DynamicGraphModel(nn.Module):
    """Динамическая модель PyTorch, исполняющая граф узлов."""
    def __init__(self, layers, connections, execution_order):
        super().__init__()
        pass