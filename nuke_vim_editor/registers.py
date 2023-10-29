import json
from typing import Any, Dict, Literal, TypedDict

from PySide2.QtGui import QClipboard


def increment(index: int) -> str:
    return chr(ord('a') + index - 9) if index >= 9 else str(index + 1)


class __Registers:
    _registers: Dict[str, str] = {}
    _register_index = 0

    @classmethod
    def get(cls, name: str):
        return cls._registers.get(name, '')

    @classmethod
    def get_all(cls):
        return cls._registers.copy()

    @classmethod
    def clear(cls):
        cls._registers.clear()
        cls._register_index = 0

    @classmethod
    def add(cls, text: str):
        z_index = 34
        if cls._register_index >= z_index:
            cls._register_index = 0

        if cls._registers.get(increment(cls._register_index - 1)) != text:
            cls._registers[increment(cls._register_index)] = text
            cls._register_index += 1

        QClipboard().setText(text, QClipboard.Clipboard)


class RegistersTypes(TypedDict):
    named: Dict[str, str]
    numbered: Dict[str, str]
    last_search: Dict[str, str]
    marks: Dict[str, int]


RegisterName = Literal['named', 'numbered', 'last_search', 'marks']


class Registers:
    _registers: RegistersTypes = {
        'named': {},
        'numbered': {},
        'last_search': {},
        'marks': {},
    }

    def __new__(cls, *args: Any, **kwargs: Any):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Registers, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # TODO: Expose this as a setting
        if 'persistent_registers':
            self._load()
        else:
            self.clear()

    def _load(self):
        with open('registers.json') as f:
            data = json.load(f)
            if data:
                self._registers = data

    def _save(self):
        with open('registers.json', 'w') as f:
            json.dump(self._registers, f)

    def update(self, name: RegisterName, key: str, value: Any) -> None:
        self._registers[name][key] = value
        self._save()

    def get(self, name: RegisterName, key: str) -> Any:
        return self._registers[name].get(key, '')

    def clear(self):
        for register in self._registers.values():
            register.clear()
        self._save()
