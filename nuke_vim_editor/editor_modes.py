from enum import Enum, auto
from typing import List, cast

from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt, QEvent, QObject
from PySide2.QtWidgets import QPlainTextEdit

from .handlers_types import NormalModeHandlerType


class Modes(Enum):
    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()


class EditorMode:
    mode = Modes.NORMAL


class NormalMode(QObject):
    def __init__(self, editor: QPlainTextEdit, handlers: List[NormalModeHandlerType]):
        super().__init__()

        self._editor = editor
        self._handlers = [handler(self._editor) for handler in handlers]

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            return False

        if EditorMode.mode == Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress:
            cursor = watched.textCursor()
            key_event = cast(QKeyEvent, event)
            for handler in self._handlers:
                if handler.should_handle(cursor, key_event):
                    handler.handle(cursor, key_event)
            watched.setTextCursor(cursor)
            return True

        return False


class InsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()
        self.editor = editor

    def eventFilter(self, watched: QObject, event):

        if EditorMode.mode == Modes.NORMAL:
            return False

        if (
            event.type() == QEvent.KeyPress and
            (event.key() == Qt.Key_Escape and EditorMode.mode == Modes.INSERT)
        ):
            self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
            EditorMode.mode = Modes.NORMAL
            return True
        return False
