import os
import json
import pathlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import asdict, dataclass

from PySide2.QtGui import QClipboard

from .settings import Settings


class Mark(Dict[str, Any]):
    position: int
    line: str


@dataclass
class RegistersData:
    named: Dict[str, str]
    clipboard: List[str]
    last_search: str
    marks: Dict[str, Mark]


class Clipboard:
    """Clipboard history.

    This class is used to store the clipboard history. It is used to store the
    text copied from the editor. The size of the clipboard is defined in the
    settings but it can be overriden at runtime.

    >>> previous_history = ['hello', 'world']
    >>> clipboard = Clipboard(previous_history)
    >>> clipboard.size = 3
    >>> clipboard.add('foo')
    >>> clipboard.add('bar')
    >>> clipboard
    >>> ['bar', 'foo', 'hello']

    """

    def __init__(self, previous_history: Optional[List[str]] = None) -> None:
        self.history: List[str] = previous_history or []
        self.size = Settings.clipboard_size

    def add(self, item: str):
        # don't add the same item twice in a row
        if self.history and item == self.history[0]:
            return

        self.history.insert(0, item)
        self.history = self.history[:self.size]

        if Settings.copy_to_system_clipboard:
            item = item.replace('<LINE_COPY>', '\n')
            QClipboard().setText(item)

    def get(self, index: int):
        return self.history[index] if 0 <= index < len(self.history) else None

    def __repr__(self):
        return str(self.history)


class RegisterFileInterface(ABC):
    @abstractmethod
    def load(self) -> RegistersData: ...

    @abstractmethod
    def save(self, registers: RegistersData) -> None: ...


class RegisterFile(RegisterFileInterface):

    def __init__(self, register_file: pathlib.Path) -> None:
        self._register_file = register_file

    def load(self) -> RegistersData:
        if not self._register_file.exists():
            registers = RegistersData(
                named={},
                clipboard=[],
                last_search='',
                marks={},
            )
            self.save(registers)
            return registers

        with self._register_file.open() as f:
            return RegistersData(**json.load(f))

    def save(self, registers: RegistersData):
        with self._register_file.open('w') as f:
            json.dump(asdict(registers), f, indent=4)


class _Registers:

    def __init__(self, register_file: RegisterFileInterface):
        self.registers_file = register_file
        self.registers = register_file.load()

        self._clipboard = Clipboard(self.registers.clipboard)
        self._named_register: Optional[str] = None

    def _push_to_clipboard(self, value: str):
        self._clipboard.add(value)
        self.registers.clipboard = self._clipboard.history
        self.registers_file.save(self.registers)

    def add_mark(self, key: str, text: str, pos: int) -> None:
        self.registers.marks[key] = Mark(position=pos, line=text)
        self.registers_file.save(self.registers)

    def get_mark(self, key: str) -> Optional[Mark]:
        return self.registers.marks.get(key)

    def add_last_search(self, value: str) -> None:
        self.registers.last_search = value
        self._push_to_clipboard(value)

    def set_named_register(self, key: str) -> None:
        self._named_register = key

    def get_numbered_register_value(self, index: int) -> Optional[str]:
        try:
            return self.registers.clipboard[index]
        except IndexError:
            return None

    def get_named_register_value(self) -> Optional[str]:
        key = self._named_register

        if not key:
            return self.registers.clipboard[0]

        if key == '/':
            return self.registers.last_search

        return self.registers.named.get(key)

    def add(self, value: str) -> None:
        if value.isspace():
            return

        if self._named_register:
            self.registers.named[self._named_register] = value

        self._push_to_clipboard(value)
        self._named_register = None

    def clear(self) -> None:

        self.registers.marks = {}
        self.registers.named = {}
        self.registers.clipboard = []
        self.registers.last_search = ''

        self.registers_file.save(self.registers)

    def get_clipboard(self) -> List[str]:
        return self.registers.clipboard

    def get_named_register(self) -> Dict[str, str]:
        return self.registers.named

    def get_marks(self) -> Dict[str, Mark]:
        return self.registers.marks


def get_register():
    env_path = os.getenv('REGISTER_DIR')
    path = env_path or pathlib.Path(__file__).parent.parent
    return pathlib.Path(path) / 'registers.json'


Registers = _Registers(RegisterFile(get_register()))
