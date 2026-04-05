from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class BaseProperty:
    """Базовый класс для свойств узла."""
    label: str
    default: Any


@dataclass
class IntProperty(BaseProperty):
    """Свойство целочисленного типа."""
    default: int = 0
    min_value: int = 0
    max_value: int = 100


@dataclass
class FloatProperty(BaseProperty):
    """Свойство вещественного типа."""
    default: float = 0.0
    min_value: float = 0.0
    max_value: float = 10.0
    step: float = 0.01


@dataclass
class TextProperty(BaseProperty):
    """Свойство текстового типа."""
    default: str = ""
    placeholder: str = ""


@dataclass
class ComboProperty(BaseProperty):
    """Свойство типа выпадающий список."""
    default: str = "1"
    options: list[str] = field(default_factory=lambda: ["1", "2", "3"])


@dataclass
class CheckboxProperty(BaseProperty):
    """Свойство типа чекбокс."""
    default: bool = True


@dataclass
class SliderProperty(BaseProperty):
    """Свойство типа ползунок."""
    default: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    step: float = 0.01

Property = Union[IntProperty, FloatProperty, TextProperty, ComboProperty, CheckboxProperty, SliderProperty]