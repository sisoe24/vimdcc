import contextlib
from enum import Enum, auto
from typing import List, cast

from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt, QEvent, QObject, QTimer, Signal
from PySide2.QtWidgets import QPlainTextEdit

from .handlers_types import NormalModeHandlerType
from .status_bar import status_bar


class Modes(Enum):
    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()
    WAIT_FOR_SECOND_KEY = auto()


class EditorMode:
    mode = Modes.NORMAL


class EditorKeyTimeout:
    timeout = 200


class NormalMode(QObject):

    on_status_bar_updated = Signal(str, str)

    operators = [
        Qt.Key_C,
        Qt.Key_D,
        Qt.Key_Y,
    ]

    mdifiers = {
        'shift': Qt.ShiftModifier,
        'ctrl': Qt.ControlModifier,
        'alt': Qt.AltModifier,
        'meta': Qt.MetaModifier,
    }

    def __init__(self, editor: QPlainTextEdit, handlers: List[NormalModeHandlerType]):
        super().__init__()

        self._editor = editor
        self._handlers = [handler(self._editor) for handler in handlers]

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reset_key_sequence)

        self.key_sequence = ""
        self.state = Modes.NORMAL

    def _reset_key_sequence(self):
        self.key_sequence = ""

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode == Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress:
            cursor = watched.textCursor()
            key_event = cast(QKeyEvent, event)

            modifiers = key_event.modifiers()
            modifiers_name = [
                name for name, modifier in self.mdifiers.items()
                if modifiers & modifier
            ]

            self.key_sequence += key_event.text()
            status_bar.emit("NORMAL", self.key_sequence)

            if key_event.key() == Qt.Key_Escape:
                self.state = Modes.NORMAL
                self.key_sequence = ""
                status_bar.emit("NORMAL", self.key_sequence)
                return True

            for handler in self._handlers:

                if not handler.should_handle(cursor, key_event, self.key_sequence):
                    continue

                self.state = handler.handle(cursor, self.key_sequence, modifiers_name, key_event)
                if self.state:
                    break

            if self.state:
                watched.setTextCursor(cursor)
                self.key_sequence = ""

            return True

        return False


class InsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()
        self.editor = editor

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode == Modes.NORMAL:
            return False

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            status_bar.emit("NORMAL", "")
            self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
            EditorMode.mode = Modes.NORMAL
            return True
        return False
