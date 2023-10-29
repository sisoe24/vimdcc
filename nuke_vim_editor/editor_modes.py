import json
from typing import List, Union, Optional, cast

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtCore import Qt, QEvent, QTimer, QObject
from PySide2.QtWidgets import QPlainTextEdit

from .registers import Registers
from .status_bar import status_bar
from .editor_state import Modes, EditorMode
from .handler_base import HandlerType, get_normal_handlers
from .handler_parameters import EventParams

OPERATORS = [
    Qt.Key_C,
    Qt.Key_D,
    Qt.Key_Y,
    Qt.Key_V
]

MODIFIERS = {
    'shift': Qt.ShiftModifier,
    'ctrl': Qt.ControlModifier,
    'alt': Qt.AltModifier,
    'meta': Qt.MetaModifier,
}


def extract_modifiers(
    modifiers: Union[Qt.KeyboardModifiers, Qt.KeyboardModifier]
) -> List[str]:
    return [
        name for name, modifier in MODIFIERS.items()
        if modifiers & modifier
    ]


class InsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode != Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            status_bar.emit('NORMAL', '')
            self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
            EditorMode.mode = Modes.NORMAL
            return True

        return False


class CommandMode(QObject):

    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.key_sequence = ''

    def execute_command(self, command: str):
        # TODO: Add python
        # TODO: Add Nuke
        # TODO: Add clear registers
        # TODO: Add clear marks

        commands = {
            'registers': lambda: print(Registers.get_all()),
            'marks': self.get_marks
        }
        commands.get(command.strip(), lambda: print('Unknown command'))()

    def get_marks(self):
        with open('marks.json') as f:
            print(json.load(f))

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode != Modes.COMMAND:
            return False

        return self.parse_keys(event) if event.type() == QEvent.KeyPress else True

    def parse_keys(self, event: QEvent):

        key_event = cast(QKeyEvent, event)
        self.key_sequence += key_event.text()
        status_bar.emit('COMMAND', self.key_sequence)

        if key_event.key() == Qt.Key_Escape:
            return self.exit_mode()

        if key_event.key() == Qt.Key_Return:
            self.execute_command(self.key_sequence)
            self.key_sequence = ''
            return self.exit_mode()

        if key_event.key() == Qt.Key_Backspace:
            self.key_sequence = self.key_sequence[:-1]
            status_bar.emit('COMMAND', self.key_sequence)
            return True

        return True

    def exit_mode(self):
        status_bar.emit('NORMAL', '')
        self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
        EditorMode.mode = Modes.NORMAL
        return True


class SearchMode(QObject):

    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.key_sequence = ''

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert False, 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode != Modes.SEARCH:
            return False

        return self.parse_keys(watched, event) if event.type() == QEvent.KeyPress else True

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent):

        cursor = editor.textCursor()
        key_event = cast(QKeyEvent, event)
        self.key_sequence += key_event.text()
        status_bar.emit('SEARCH', self.key_sequence)

        if key_event.key() == Qt.Key_Escape:
            return self.exit_mode()

        if key_event.key() == Qt.Key_Return:
            return self.go_to_text(editor, cursor)

        if key_event.key() == Qt.Key_Backspace:
            self.key_sequence = self.key_sequence[:-1]
            status_bar.emit('SEARCH', self.key_sequence)
            return True

        return True

    def go_to_text(self, editor: QPlainTextEdit, cursor: QTextCursor):
        document = editor.document().toPlainText()
        find = document.find(self.key_sequence.strip())
        cursor.setPosition(find)
        self.editor.setTextCursor(cursor)
        self.key_sequence = ''
        return self.exit_mode()

    def exit_mode(self):
        status_bar.emit('NORMAL', '')
        self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
        EditorMode.mode = Modes.NORMAL
        return True


class NormalMode(QObject):

    def __init__(self, editor: QPlainTextEdit, handlers: Optional[List[HandlerType]] = None, parent=None):
        super().__init__(parent)

        self.editor = editor

        handlers = handlers or get_normal_handlers()

        self._handlers = [handler(self.editor) for handler in handlers]

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.reset_key_sequence)

        self.key_sequence = ''
        self.internal_state = ''

    def reset_key_sequence(self):
        self.key_sequence = ''

    def arrow_keys(self, cursor: QTextCursor, key_event: QKeyEvent):
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
            assert False, 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode not in [Modes.NORMAL, Modes.VISUAL, Modes.VISUAL_LINE, Modes.YANK]:
            return False

        if event.type() == QEvent.KeyPress:
            return self.parse_keys(watched, event)
        return False

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent):

        cursor = editor.textCursor()
        position = cursor.position()
        key_event = cast(QKeyEvent, event)
        modifiers = extract_modifiers(key_event.modifiers())

        self.key_sequence += key_event.text()
        status_bar.emit('NORMAL', self.key_sequence)

        if key_event.key() == Qt.Key_Escape:
            self.change_mode(Modes.NORMAL, '')
            cursor.clearSelection()
            self.editor.setTextCursor(cursor)
            return True

        if self.key_sequence == ':':
            self.change_mode(Modes.COMMAND, self.key_sequence)
            return True

        if self.key_sequence in ['/', '?']:
            self.change_mode(Modes.SEARCH, self.key_sequence)
            return True

        if self.key_sequence == 'V':
            # self.change_mode(Modes.VISUAL_LINE, self.key_sequence)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            editor.setTextCursor(cursor)
            self.change_mode(Modes.VISUAL, self.key_sequence)
            EditorMode.mode = Modes.VISUAL_LINE
            return True

        if self.key_sequence == 'v':
            self.change_mode(Modes.VISUAL, self.key_sequence)
            return True

        if self.key_sequence == 'y' and not EditorMode.mode == Modes.YANK:
            EditorMode.mode = Modes.YANK
            self.key_sequence = ''

            # self.change_mode(Modes.YANK, self.key_sequence)
            return True

        if self.key_sequence == 'u':
            self.reset_key_sequence()
            self.editor.undo()
            return True

        if 'ctrl' in modifiers and self.key_sequence == 'r':
            self.reset_key_sequence()
            self.editor.redo()
            return True

        if self.key_sequence == 'p':
            self.reset_key_sequence()
            self.editor.paste()
            return True

        if self.arrow_keys(cursor, key_event):
            editor.setTextCursor(cursor)
            return True

        execute = False
        for handler in self._handlers:

            params = EventParams(
                cursor=cursor,
                keys=self.key_sequence,
                modifiers=modifiers,
                event=key_event,
                mode=EditorMode.mode,
            )

            if not handler.should_handle(params):
                continue

            if handler.handle(params):
                editor.setTextCursor(cursor)
                self.reset_key_sequence()
                execute = True
                break

        if execute and EditorMode.mode == Modes.YANK:
            text = cursor.selectedText()

            cursor.clearSelection()
            cursor.setPosition(position)
            editor.setTextCursor(cursor)

            EditorMode.mode = Modes.NORMAL
            return True

        return True


EDITOR_MODES = [
    NormalMode,
    SearchMode,
    InsertMode,
    CommandMode,
]
