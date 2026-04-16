import black
from jinja2 import Environment, FileSystemLoader

from config import TEMPLATES_DIR


class DatasetCodeGenerator:
    """Генерирует Python-код для загрузки и препроцессинга датасета."""

    _NORM_MAP = {0: "None", 1: "MinMax", 2: "Z-Score"}

    def __init__(self, dataset_config: dict):
        self.config = dataset_config
        self.dataset_name = "Iris" if self.config.get("combo_index", 0) == 0 else "MNIST"
        self.norm_type = self._NORM_MAP.get(self.config.get("normalization", 0), "None")
        self.train_split = self.config.get("train_split", 80) / 100.0
        self.stratified = self.config.get("stratified", True)

    def generate(self) -> str:
        """Основной метод генерации кода."""
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        if self.dataset_name == "MNIST":
            template = env.get_template("dataset_mnist.jinja2")
            context = {}
        else:
            template = env.get_template("dataset_iris.jinja2")
            context = {
                "train_split": self.train_split,
                "norm_type": self.norm_type,
                "stratified": self.stratified
            }

        raw_code = template.render(**context)
        return black.format_str(raw_code, mode=black.Mode())
