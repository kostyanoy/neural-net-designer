from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class BaseProperty:
    label: str
    default: Any


@dataclass
class IntProperty(BaseProperty):
    default: int = 0
    min_value: int = 0
    max_value: int = 100


@dataclass
class FloatProperty(BaseProperty):
    default: float = 0.0
    min_value: float = 0.0
    max_value: float = 10.0
    step: float = 0.01


@dataclass
class TextProperty(BaseProperty):
    default: str = ""
    placeholder: str = ""


@dataclass
class ComboProperty(BaseProperty):
    default: str = "1"
    options: list[str] = field(default_factory=lambda: ["1", "2", "3"])


@dataclass
class CheckboxProperty(BaseProperty):
    default: bool = True


@dataclass
class SliderProperty(BaseProperty):
    default: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    step: float = 0.01

Property = Union[IntProperty, FloatProperty, TextProperty, ComboProperty, CheckboxProperty, SliderProperty]