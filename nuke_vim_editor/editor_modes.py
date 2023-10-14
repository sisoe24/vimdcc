from typing import List, cast

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtCore import Qt, QEvent, QTimer, QObject
from PySide2.QtWidgets import QPlainTextEdit

from .marks import Marks
from .registers import Registers
from .status_bar import status_bar
from ._types import NormalModeHandlerType, Modes, EventParams


class EditorMode:
    mode = Modes.NORMAL


class NormalMode(QObject):

    operators = [
        Qt.Key_C,
        Qt.Key_D,
        Qt.Key_Y,
        Qt.Key_V
    ]

    modifiers = {
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
        self._timer.timeout.connect(self.reset_key_sequence)

        self.key_sequence = ""
        self.state = Modes.NORMAL

    def reset_key_sequence(self):
        self.key_sequence = ""

    def arrow_keys(self, cursor: QTextCursor, key_event: QKeyEvent):
        # TODO: Add settings to enable/disable arrow keys
        key = key_event.key()

        if key == Qt.Key_Left:
            cursor.movePosition(QTextCursor.Left)
            return True
        if key == Qt.Key_Right:
            cursor.movePosition(QTextCursor.Right)
            return True
        if key == Qt.Key_Up:
            cursor.movePosition(QTextCursor.Up)
            return True
        if key == Qt.Key_Down:
            cursor.movePosition(QTextCursor.Down)
            return True
        return False

    def change_mode(self, mode: Modes, keys: str):
        status_bar.emit(mode.value, keys)
        EditorMode.mode = mode
        self.reset_key_sequence()

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode not in [Modes.NORMAL, Modes.VISUAL]:
            return False

        if event.type() == QEvent.KeyPress:
            return self.parse_keys(watched, event)
        return False

    def parse_keys(self, watched: QPlainTextEdit, event: QEvent):
        cursor = watched.textCursor()
        key_event = cast(QKeyEvent, event)
        modifiers = [
            name for name, modifier in self.modifiers.items()
            if key_event.modifiers() & modifier
        ]

        self.key_sequence += key_event.text()
        # status_bar.emit("NORMAL", self.key_sequence)

        if key_event.key() == Qt.Key_Escape:
            self.change_mode(Modes.NORMAL, "")
            cursor.clearSelection()
            self._editor.setTextCursor(cursor)
            return True

        if self.key_sequence == ":":
            self.change_mode(Modes.COMMAND, self.key_sequence)
            return True

        if self.key_sequence == "V" and modifiers == ["shift"]:
            self.change_mode(Modes.VISUAL_LINE, self.key_sequence)
            return True

        if self.key_sequence == "v":
            self.change_mode(Modes.VISUAL, self.key_sequence)
            return True

        if key_event.key() == Qt.Key_U:
            self.reset_key_sequence()
            self._editor.undo()
            return True

        if key_event.key() == Qt.Key_R and modifiers & Qt.ControlModifier:
            self.reset_key_sequence()
            self._editor.redo()
            return True

        if key_event.key() == Qt.Key_P:
            self.reset_key_sequence()
            self._editor.paste()
            return True

        if self.arrow_keys(cursor, key_event):
            watched.setTextCursor(cursor)
            return True

        for handler in self._handlers:

            params = EventParams(
                cursor=cursor,
                keys=self.key_sequence,
                modifiers=modifiers,
                event=key_event,
                mode=EditorMode.mode,
                visual=EditorMode.mode == Modes.VISUAL,
            )

            if not handler.should_handle(params):
                continue

            self.state = handler.handle(params)
            if self.state:
                break

        if self.state:
            watched.setTextCursor(cursor)
            self.reset_key_sequence()

        return True


class InsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode != Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            status_bar.emit("NORMAL", "")
            self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
            EditorMode.mode = Modes.NORMAL
            return True

        return False


class VisualLineMode(QObject):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode != Modes.VISUAL_LINE:
            return False

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            status_bar.emit("NORMAL", "")
            self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
            EditorMode.mode = Modes.NORMAL
            return True

        return False


class CommandMode(QObject):

    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.key_sequence = ""

    def execute_command(self, command: str):
        # TODO: Add python command
        # TODO: Add Nuke command

        commands = {
            "registers": lambda: print(Registers.get_all()),
            "marks": lambda: print(Marks.get_all())
        }
        commands.get(command.strip(), lambda: print("Unknown command"))()

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, "This event filter should only be installed on a QPlainTextEdit"

        if EditorMode.mode != Modes.COMMAND:
            return False

        return self.parse_keys(event) if event.type() == QEvent.KeyPress else True

    def parse_keys(self, event: QEvent):

        key_event = cast(QKeyEvent, event)
        self.key_sequence += key_event.text()
        status_bar.emit("COMMAND", self.key_sequence)

        if key_event.key() == Qt.Key_Escape:
            return self.exit_mode()

        if key_event.key() == Qt.Key_Return:
            self.execute_command(self.key_sequence)
            self.key_sequence = ""
            return self.exit_mode()

        if key_event.key() == Qt.Key_Backspace:
            self.key_sequence = self.key_sequence[:-1]
            status_bar.emit("COMMAND", self.key_sequence)
            return True

        return True

    def exit_mode(self):
        status_bar.emit("NORMAL", "")
        self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
        EditorMode.mode = Modes.NORMAL
        return True
