from typing import Dict, Optional, TypedDict


class MarkData(TypedDict):
    text: str
    position: int


MarkItem = Dict[str, MarkData]


class Marks:
    _marks: MarkItem = {}

    @classmethod
    def get(cls, name: str) -> Optional[MarkData]:
        return cls._marks.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, MarkData]:
        return cls._marks.copy()

    @classmethod
    def clear(cls):
        cls._marks.clear()

    @classmethod
    def add(cls, key: str, data: MarkData):
        cls._marks[key] = data
