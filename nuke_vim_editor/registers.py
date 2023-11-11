import json
from typing import (Any, Dict, List, Generic, Literal, TypeVar, Optional,
                    TypedDict)


def increment(index: int) -> str:
    return chr(ord('a') + index - 9) if index >= 9 else str(index + 1)


class _NumberedBuffer:
    def __init__(self, previous_history: list[str], size: int = 10):
        self.history: list[str] = previous_history or []
        self.size = size

    def add(self, item: str):
        # don't add the same item twice
        if self.history and item == self.history[0]:
            return

        self.history.insert(0, item)
        self.history = self.history[: self.size]

    def get(self, index: int):
        return self.history[index] if 0 <= index < len(self.history) else None

    def __repr__(self):
        return str(self.history)


class Mark(TypedDict):
    position: int
    line: str


class RegistersTypes(TypedDict):
    named: Dict[str, str]
    numbered: List[str]
    last_search: str
    marks: Dict[str, Mark]


RegisterName = Literal['named', 'last_search', 'marks']

T = TypeVar('T', bound=RegisterName)


class _Registers:
    registers: RegistersTypes = {
        'named': {},
        'numbered': [],
        'last_search': '',
        'marks': {},
    }

    def __init__(self):
        self._load()
        self._named_buffer = _NumberedBuffer(self.registers['numbered'])
        self._named_register: Optional[str] = None

    def _load(self):
        with open('registers.json') as f:
            data = json.load(f)
            if data:
                self.registers = data

    def _save(self):
        with open('registers.json', 'w') as f:
            json.dump(self.registers, f, indent=4)

    def _push_to_clipboard(self, value: str):
        self._named_buffer.add(value)
        self.registers['numbered'] = self._named_buffer.history
        self._save()

    def add_mark(self, key: str, text: str, pos: int) -> None:
        self.registers['marks'][key] = {'position': pos, 'line': text}
        self._save()

    def get_mark(self, key: str) -> Optional[Mark]:
        return self.registers['marks'].get(key)

    def add_last_search(self, value: str) -> None:
        self.registers['last_search'] = value
        self._push_to_clipboard(value)

    def set_named_register(self, key: str) -> None:
        self._named_register = key

    def get_numbered_register_value(self, index: int) -> Optional[str]:
        return self.registers['numbered'][index]

    def get_named_register_value(self) -> Optional[str]:
        key = self._named_register

        if not key:
            self.registers['numbered'][0]
            return

        if key == '/':
            return self.registers['last_search']

        return self.registers['named'].get(key)

    def push(self, value: str) -> None:
        if self._named_register:
            self.registers['named'][self._named_register] = value

        self._push_to_clipboard(value)
        self._named_register = None

    def get_register(self, name: RegisterName) -> Any:
        return self.registers[name]

    def clear(self):
        for register in self.registers.values():
            register.clear()
        self._save()


Registers = _Registers()
