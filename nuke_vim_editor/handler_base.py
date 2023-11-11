
from abc import ABC, abstractmethod
from typing import Any, List, Type, TypeVar, Callable

from PySide2.QtWidgets import QPlainTextEdit

from .registers import Registers
from .status_bar import status_bar
from .editor_modes import Modes
from .editor_state import EditorMode
from .handler_parameters import HandlerParams

HandlerType = Callable[[QPlainTextEdit], Any]

_NORMAL_HANDLERS: List[HandlerType] = []


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor
        self.registers = Registers

    def add_to_clipboard(self, text: str):
        self.registers.push(text)

    def get_state(self):
        return EditorMode.mode

    def set_state(self, state: Modes):
        EditorMode.mode = state

    def to_normal_mode(self):
        status_bar.emit('NORMAL', '')
        EditorMode.mode = Modes.NORMAL
        self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
        self.editor.viewport().update()

    def to_insert_mode(self):
        status_bar.emit('INSERT', '')
        EditorMode.mode = Modes.INSERT
        self.editor.setCursorWidth(2)
        self.editor.viewport().update()

    def should_handle(self, params: HandlerParams) -> bool:
        return True

    @abstractmethod
    def handle(self, params: HandlerParams) -> bool:
        """Handle the key sequence and return True if the key sequence was handled.

        If the key sequence was handled, the cursor will be updated and the key sequence will be reset.

        Args:
            params (EventParams): The event parameters
        Returns:
            bool: True if the key sequence was handled, False otherwise
        """
        ...


T = TypeVar('T', bound=BaseHandler)


def register_normal_handler(handler: Type[T]) -> Type[T]:
    _NORMAL_HANDLERS.append(handler)
    return handler


def get_normal_handlers() -> List[HandlerType]:
    return _NORMAL_HANDLERS
