
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Literal, TypeVar, TypedDict

from PySide2.QtWidgets import QPlainTextEdit

from ._types import Modes, EventParams, HandlerType
from .status_bar import status_bar
from .editor_state import EditorState

_NORMAL_HANDLERS: List[HandlerType] = []
_COMMAND_HANDLERS: List[HandlerType] = []
_VISUAL_LINE_HANDLERS: List[HandlerType] = []


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
        print('➡ name :', name)
        return self._registers[name].get(key, '')

    def clear(self):
        for register in self._registers.values():
            register.clear()
        self._save()


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor
        self.registers = Registers()

    def get_state(self):
        return EditorState.mode

    def set_state(self, state: Modes):
        EditorState.mode = state

    def to_normal_mode(self):
        status_bar.emit('NORMAL', '')
        EditorState.mode = Modes.NORMAL
        self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
        self.editor.viewport().update()

    def to_insert_mode(self):
        status_bar.emit('INSERT', '')
        EditorState.mode = Modes.INSERT
        self.editor.setCursorWidth(2)
        self.editor.viewport().update()

    def should_handle(self, params: EventParams) -> bool:
        return True

    @abstractmethod
    def handle(self, params: EventParams) -> bool: ...
    """Handle the key sequence and return True if the key sequence was handled.

    If the key sequence was handled, the cursor will be updated and the key sequence will be reset.

    Args:
        params (EventParams): The event parameters
    Returns:
        bool: True if the key sequence was handled, False otherwise

    """


T = TypeVar('T', bound=BaseHandler)


def register_normal_handler(handler: Type[T]) -> Type[T]:
    _NORMAL_HANDLERS.append(handler)
    return handler


def register_command_handler(handler: Type[T]) -> Type[T]:
    _COMMAND_HANDLERS.append(handler)
    return handler


def register_visual_line_handler(handler: Type[T]) -> Type[T]:
    _VISUAL_LINE_HANDLERS.append(handler)
    return handler


def get_normal_handlers() -> List[HandlerType]:
    return _NORMAL_HANDLERS


def get_command_handlers() -> List[HandlerType]:
    return _COMMAND_HANDLERS


def get_visual_line_handlers() -> List[HandlerType]:
    return _VISUAL_LINE_HANDLERS
