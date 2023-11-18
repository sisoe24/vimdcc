import os
import json
import pathlib
from typing import (Any, Dict, List, Literal, Optional, Protocol, TypedDict,
                    overload)


def increment(index: int) -> str:
    return chr(ord('a') + index - 9) if index >= 9 else str(index + 1)


class Mark(TypedDict):
    position: int
    line: str


class RegistersTypes(TypedDict):
    named: Dict[str, str]
    numbered: List[str]
    last_search: str
    marks: Dict[str, Mark]


RegisterName = Literal['named', 'last_search', 'marks', 'numbered']


class Clipboard:
    def __init__(self, previous_history: List[str], size: int = 10):
        self.history: List[str] = previous_history or []
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


class RegisterFileProtocol(Protocol):
    def load(self) -> RegistersTypes: ...
    def save(self, registers: RegistersTypes) -> None: ...


class RegisterFile:
    registers: RegistersTypes = {
        'named': {},
        'numbered': [],
        'last_search': '',
        'marks': {},
    }

    def __init__(self, register_file: pathlib.Path) -> None:
        self._register_file = register_file

    def load(self):
        if not self._register_file.exists():
            self.save(self.registers)

        with self._register_file.open() as f:
            return json.load(f)

    def save(self, registers: RegistersTypes):
        with self._register_file.open('w') as f:
            json.dump(registers, f, indent=4)


class _Registers:
    registers: RegistersTypes = {
        'named': {},
        'numbered': [],
        'last_search': '',
        'marks': {},
    }

    def __init__(self, register_file: RegisterFileProtocol):
        self.registers_file = register_file
        self.registers = register_file.load()

        self._clipboard = Clipboard(self.registers['numbered'])
        self._named_register: Optional[str] = None

    def _push_to_clipboard(self, value: str):
        self._clipboard.add(value)
        self.registers['numbered'] = self._clipboard.history
        self.registers_file.save(self.registers)

    def add_mark(self, key: str, text: str, pos: int) -> None:
        self.registers['marks'][key] = {'position': pos, 'line': text}
        self.registers_file.save(self.registers)

    def get_mark(self, key: str) -> Optional[Mark]:
        return self.registers['marks'].get(key)

    def add_last_search(self, value: str) -> None:
        self.registers['last_search'] = value
        self._push_to_clipboard(value)

    def set_named_register(self, key: str) -> None:
        self._named_register = key

    def get_numbered_register_value(self, index: int) -> Optional[str]:
        try:
            return self.registers['numbered'][index]
        except IndexError:
            return None

    def get_named_register_value(self) -> Optional[str]:
        key = self._named_register

        if not key:
            return self.registers['numbered'][0]

        if key == '/':
            return self.registers['last_search']

        return self.registers['named'].get(key)

    def add(self, value: str) -> None:
        if value.isspace():
            # TODO: add a warning
            return

        if self._named_register:
            self.registers['named'][self._named_register] = value

        self._push_to_clipboard(value)
        self._named_register = None

    @overload
    def get_register(self, name: Literal['marks']) -> Mark: ...

    @overload
    def get_register(self, name: Literal['last_search']) -> str: ...

    @overload
    def get_register(self, name: Literal['numbered']) -> List[str]: ...

    @overload
    def get_register(self, name: Literal['named']) -> Dict[str, str]: ...

    @overload
    def get_register(self, name: str) -> Any: ...

    def get_register(self, name: str) -> Any:
        return self.registers[name]


def get_register():
    env_path = os.getenv('REGISTER_DIR')
    path = env_path or pathlib.Path(__file__).parent.parent
    return pathlib.Path(path) / 'registers.json'


Registers = _Registers(RegisterFile(get_register()))
