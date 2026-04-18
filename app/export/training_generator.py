import black
from jinja2 import Environment, FileSystemLoader

from app.config import TEMPLATES_DIR

class TrainingCodeGenerator:
    """Генерирует Python-код для обучения модели."""

    OPTIMIZER_MAP = {
        "Adam": "Adam",
        "SGD": "SGD",
        "AdamW": "AdamW",
        "RMSprop": "RMSprop",
        "Adagrad": "Adagrad"
    }

    LOSS_MAP = {
        "CrossEntropyLoss": "CrossEntropyLoss",
        "MSELoss": "MSELoss",
        "BCELoss": "BCELoss",
        "BCEWithLogitsLoss": "BCEWithLogitsLoss"
    }

    def __init__(self, training_config: dict, model_class_name: str = "GeneratedModel"):
        self.config = training_config
        self.model_class_name = model_class_name

    def generate(self) -> str:
        optimizer_name = self.OPTIMIZER_MAP[self.config["optimizer"]]
        loss_name = self.LOSS_MAP[self.config["loss_function"]]
        selected_metrics = [m.lower().replace("-", "_") for m in self.config["metrics"]]

        context = {
            "model_class_name": self.model_class_name,
            "batch_size": self.config["batch_size"],
            "optimizer_name": optimizer_name,
            "learning_rate": self.config["learning_rate"],
            "weight_decay": self.config["weight_decay"],
            "loss_function_name": loss_name,
            "epochs": self.config["epochs"],
            "selected_metrics": selected_metrics
        }

        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("training.jinja2")
        raw_code = template.render(**context)
        return black.format_str(raw_code, mode=black.Mode())

