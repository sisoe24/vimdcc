
from abc import ABC, abstractmethod
from typing import List

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from .editor_modes import Modes, EditorMode
from .handlers_types import NormalModeHandlerType

_NORMAL_HANDLERS: List[NormalModeHandlerType] = []


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def editor_state(self):
        return EditorMode.mode

    def set_state(self, state: Modes):
        EditorMode.mode = state

    def to_insert_mode(self):
        self.set_state(Modes.INSERT)
        self.editor.setCursorWidth(2)
        self.editor.viewport().update()

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent) -> bool:
        return True

    @abstractmethod
    def handle(self, cursor: QTextCursor, event: QKeyEvent): ...


def register_normal_handler(handler: NormalModeHandlerType):
    _NORMAL_HANDLERS.append(handler)


def get_normal_handlers() -> List[NormalModeHandlerType]:
    return _NORMAL_HANDLERS
