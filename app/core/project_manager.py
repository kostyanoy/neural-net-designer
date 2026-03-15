import json
from datetime import datetime
from pathlib import Path

from NodeGraphQt import NodeGraph
from PyQt5.QtCore import QObject, pyqtSignal

from config import VERSION


class ProjectManager(QObject):
    """Управление состоянием проекта: сохранение, загрузка, валидация."""

    project_loaded = pyqtSignal(dict)
    project_saved = pyqtSignal(str)
    project_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_project = None
        self.project_path = None

    def create_new_project(self, name: str = "Untitled") -> dict:
        """Создать новый проект."""
        self.current_project = self._create_empty_project(name)
        self.project_path = None
        self.project_loaded.emit(self.current_project)
        self.project_changed.emit()
        return self.current_project

    def _create_empty_project(self, name: str = "Untitled") -> dict:
        """Создать структуру пустого проекта."""
        return {
            "metadata": {
                "name": name,
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "app_version": VERSION
            },
            "architecture": {}
        }

    def serialize_graph(self, graph: NodeGraph) -> dict:
        """Сериализовать граф NodeGraphQt в формат проекта."""
        data = graph.serialize_session()
        return {
            "nodes": data.get("nodes", []),
            "connections": data.get("connections", [])
        }

    def deserialize_graph(self, graph: NodeGraph, data: dict):
        """Восстановить граф из данных проекта."""
        try:
            graph.deserialize_session(data["architecture"])
        except Exception as e:
            print(f"Error deserializing graph: {e}")

    def save_project(self, path: str, graph: NodeGraph):
        """Сохранить проект в файл."""
        self.current_project["architecture"] = self.serialize_graph(graph)
        self.current_project["metadata"]["modified"] = datetime.now().isoformat()
        self.project_changed.emit()

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.current_project, f, indent=4, ensure_ascii=False)

        self.project_path = path
        self.project_saved.emit(path)

    def load_project(self, path: str) -> dict:
        """Загрузить проект из файла."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.current_project = json.load(f)
            self.project_path = path
            self.project_loaded.emit(self.current_project)
            return self.current_project
        except Exception as e:
            print(f"Error loading project: {e}")
            return {}

    def validate_graph(self, graph: NodeGraph) -> dict:
        """Валидация графа перед сохранением/обучением."""

        errors = []
        nodes = graph.all_nodes()
        if len(nodes) == 0:
            errors.append("Граф не содержит узлов")

        for node in nodes:
            has_input = len(node.inputs()) > 0
            has_output = len(node.outputs()) > 0

            is_input_unconnected = any(node.connected_input_nodes()) or not has_input
            is_output_unconnected = any(node.connected_output_nodes()) or not has_output

            if is_input_unconnected and is_output_unconnected and len(nodes) > 0:
                errors.append(f"Блок {node.name()} не соединен с остальным графом")

        return {"valid": len(errors) == 0, "errors": errors}

    def get_project_name(self) -> str:
        """Получить имя текущего проекта."""
        return self.current_project["metadata"]["name"]

    def set_project_name(self, name: str):
        """Установить имя текущего проекта"""
        self.current_project["metadata"]["name"] = name

    def update_architecture_params(self, graph: NodeGraph):
        """Обновить параметры архитектуры."""
        self.current_project["architecture"] = self.serialize_graph(graph)
        self.project_changed.emit()
