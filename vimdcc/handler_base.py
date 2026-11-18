from abc import ABC, abstractmethod
from typing import Any, List, Type, TypeVar, Callable

from ._qt import QPlainTextEdit

from .logger import LOGGER
from .registers import Registers
from .status_bar import status_bar
from .editor_mode import Modes, EditorMode
from .handler_parameters import HandlerParams

HandlerType = Callable[[QPlainTextEdit], Any]

_NORMAL_HANDLERS: List[HandlerType] = []


def set_mode(editor: QPlainTextEdit, mode: Modes):
    EditorMode.mode = mode
    status_bar.write(mode.value, '')
    editor.setCursorWidth(2 if mode == Modes.INSERT else editor.fontMetrics().horizontalAdvance(' '))
    editor.viewport().update()


class BaseHandler(ABC):
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor
        self.registers = Registers

    @property
    def mode(self):
        return EditorMode.mode

    @mode.setter
    def mode(self, state: Modes):
        EditorMode.mode = state

    def add_to_clipboard(self, text: str):
        self.registers.add(text)

    def to_normal_mode(self):
        set_mode(self.editor, Modes.NORMAL)

    def to_insert_mode(self):
        set_mode(self.editor, Modes.INSERT)

    def to_visual_mode(self):
        set_mode(self.editor, Modes.VISUAL)

    def should_handle(self, params: HandlerParams) -> bool:
        """Indicate whether the key sequence should be handled."""
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
    LOGGER.debug(f"Registering handler: {handler.__name__}")
    _NORMAL_HANDLERS.append(handler)
    return handler


def get_normal_handlers() -> List[HandlerType]:
    return _NORMAL_HANDLERS
