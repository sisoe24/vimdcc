
from abc import ABC, abstractmethod
from typing import Dict, List

from PySide2.QtWidgets import QPlainTextEdit

from .status_bar import status_bar
from .editor_modes import Modes, EditorMode
from ._types import NormalModeHandlerType, EventParams

_NORMAL_HANDLERS: List[NormalModeHandlerType] = []
_COMMAND_HANDLERS: List[NormalModeHandlerType] = []


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def editor_state(self):
        return EditorMode.mode

    def set_state(self, state: Modes):
        EditorMode.mode = state

    def to_insert_mode(self):
        status_bar.emit("INSERT", "")
        self.set_state(Modes.INSERT)
        self.editor.setCursorWidth(2)
        self.editor.viewport().update()

    def to_normal_mode(self):
        status_bar.emit("NORMAL", "")
        self.set_state(Modes.NORMAL)
        self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
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


def register_normal_handler(handler: NormalModeHandlerType):
    _NORMAL_HANDLERS.append(handler)


def get_normal_handlers() -> List[NormalModeHandlerType]:
    return _NORMAL_HANDLERS
