from datetime import datetime
from typing import Any

class Calendar:
    @classmethod
    def from_ical(cls, st: str) -> "Calendar":
        pass
    def get(self, key: str, default: Any) -> Any:
        pass
    def add(self, key: str, value: str) -> None:
        pass
    def add_component(self, component: dict[str, Any]) -> None:
        pass
    def to_ical(self) -> str:
        pass
    subcomponents: list[dict[str, Any]]

class Event(dict):
    def add(self, key: str, value: Any) -> None:
        pass

class vDate:
    def __init__(self, dt: datetime) -> None:
        pass

class vDatetime:
    def __init__(self, dt: datetime) -> None:
        pass

class vText:
    def __init__(self, dt: str) -> None:
        pass

class vCalAddress:
    def __init__(self, dt: str) -> None:
        pass
    params: dict[str, Any]
