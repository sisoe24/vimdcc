
from abc import ABC, abstractmethod
from typing import List

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from .editor_modes import Modes, EditorMode
from .handlers_types import NormalModeHandlerType
from .status_bar import status_bar

_NORMAL_HANDLERS: List[NormalModeHandlerType] = []


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor
        self.key_sequence = ""

    def editor_state(self):
        return EditorMode.mode

    def set_state(self, state: Modes):
        EditorMode.mode = state

    def get_key_sequence(self, event: QKeyEvent) -> str:
        self.key_sequence += event.text()
        return self.key_sequence

    def reset_key_sequence(self):
        self.key_sequence = ""

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

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent, key_sequence: str) -> bool:
        return True

    @abstractmethod
    def handle(self, cursor: QTextCursor, key_sequence: str,
               modifiers: List[str], event: QKeyEvent) -> bool: ...
    """Handle the key sequence and return True if the key sequence was handled.
    
    If the key sequence was handled, the cursor will be updated and the key sequence will be reset.

    Args:

        cursor (QTextCursor): The cursor of the editor
        key_sequence (str): The key sequence that was pressed (e.g. "i", "a", "w")
        modifiers (List[str]): The modifiers that were pressed (e.g. ["Shift", "Ctrl"])
        event (QKeyEvent): The event that was triggered
    
    Returns:
        bool: True if the key sequence was handled, False otherwise
    
    """


def register_normal_handler(handler: NormalModeHandlerType):
    _NORMAL_HANDLERS.append(handler)


def get_normal_handlers() -> List[NormalModeHandlerType]:
    return _NORMAL_HANDLERS
