from typing import List, Optional, cast

from PySide2.QtGui import Qt, QKeyEvent, QTextCursor
from PySide2.QtCore import QEvent, QObject
from PySide2.QtWidgets import QPlainTextEdit

from .events import EventManager
from .logger import LOGGER
from .status_bar import status_bar
from .editor_mode import Modes, EditorMode
from .handler_base import HandlerType, get_normal_handlers
from .handler_parameters import HandlerParams

# TODO: Test this module


def extract_modifiers(modifiers: Qt.KeyboardModifiers) -> List[str]:
    base_modifiers = {
        'shift': Qt.ShiftModifier,
        'ctrl': Qt.ControlModifier,
        'alt': Qt.AltModifier,
        'meta': Qt.MetaModifier,
    }

    return [name for name, modifier in base_modifiers.items() if modifiers & modifier]


class BaseFilter(QObject):
    key_sequence = ''

    def __init__(self, editor: QPlainTextEdit, allowed_modes: List[Modes], parent=None):
        super().__init__(parent)
        self.allowed_modes = allowed_modes
        self.editor = editor
        self.cursor_width = {
            'block': self.editor.fontMetrics().width(' '),
            'line': 1
        }

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            assert (
                False
            ), 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode not in self.allowed_modes:
            return False

        if event.type() == QEvent.KeyPress:
            return self.parse_keys(watched, event)

        return False

    def change_mode(self, mode: Modes, cursor_width: int, keys: str = ''):
        self.editor.setCursorWidth(cursor_width)
        EditorMode.mode = mode
        self.key_sequence = ''
        status_bar.write(mode.value, keys)
        return True

    def to_normal(self):
        return self.change_mode(Modes.NORMAL, self.cursor_width['block'])

    def to_insert(self):
        return self.change_mode(Modes.INSERT, self.cursor_width['line'])

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent) -> bool:
        raise NotImplementedError


class InsertEventFilter(BaseFilter):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(editor, [Modes.INSERT], parent)
        self.editor = editor

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent):

        key_event = cast(QKeyEvent, event)

        if event.key() == Qt.Key_Escape:
            super().to_normal()
            return True

        if key_event.text() == '®':
            self.editor.redo()
            return True

        return False


class NormalEventFilter(BaseFilter):
    operators = ['d', 'c', 'y', 'v']
    text_objects = ['i', 'a']

    def __init__(
        self, editor: QPlainTextEdit,
        handlers: Optional[List[HandlerType]] = None,
        parent=None
    ):
        super().__init__(editor, [
            Modes.NORMAL, Modes.VISUAL, Modes.VISUAL_LINE, Modes.DELETE,
            Modes.CHANGE, Modes.YANK
        ], parent)
        LOGGER.debug('Initializing normal mode')

        self.editor = editor
        LOGGER.debug(f"editor: {editor}")

        handlers = handlers or get_normal_handlers()
        self._handlers = [handler(self.editor) for handler in handlers]
        LOGGER.debug(f"handlers: {self._handlers}")

    def _set_edit_mode(self,):
        """Check if the key sequence is a edit mode.

        This is an ugly hack to check if the key sequence is a edit mode. If a
        double key is pressed, like 'd' and 'w', the first key is the edit mode
        while the second is the command. It then sets the edit mode and removes
        the first key from the sequence and passes the second key to the handlers
        to be executed.

        """
        operator = self.key_sequence[0]
        if (
            len(self.key_sequence) != 2 or
            operator not in self.operators or
            self.key_sequence[1] in [*self.text_objects, operator]
        ):
            return

        operator_modes = {
            'v': Modes.VISUAL,
            'y': Modes.YANK,
            'd': Modes.DELETE,
            'c': Modes.CHANGE,
        }

        EditorMode.mode = operator_modes[operator]
        self.key_sequence = self.key_sequence[1:]

    def arrow_keys(self, cursor: QTextCursor, key_event: QKeyEvent):
        key = key_event.key()

        arrows = {
            Qt.Key_Left: QTextCursor.Left,
            Qt.Key_Right: QTextCursor.Right,
            Qt.Key_Up: QTextCursor.Up,
            Qt.Key_Down: QTextCursor.Down,
        }
        if arrows.get(key):
            cursor.movePosition(arrows[key])
            return True

        return False

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent):
        cursor = editor.textCursor()
        key_event = cast(QKeyEvent, event)
        modifiers = extract_modifiers(key_event.modifiers())

        self.key_sequence += key_event.text().strip()
        status_bar.write('NORMAL', self.key_sequence)

        if self.key_sequence:
            self._set_edit_mode()

        # this is just temporary until I figure out how to better handle this
        if key_event.key() == Qt.Key_Return:
            EventManager.emit('execute_code')
            return True

        if key_event.key() == Qt.Key_Escape:
            super().to_normal()
            cursor.clearSelection()
            self.editor.setTextCursor(cursor)
            return True

        if key_event.key() == Qt.Key_Backspace:
            self.key_sequence = self.key_sequence[:-1]
            return True

        if self.key_sequence == 'V':
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            self.editor.setTextCursor(cursor)
            return super().change_mode(Modes.VISUAL_LINE, self.cursor_width['block'])

        if self.arrow_keys(cursor, key_event):
            self.editor.setTextCursor(cursor)
            return True

        execute = False
        for handler in self._handlers:
            params = HandlerParams(
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
                self.key_sequence = ''
                execute = True
                break

        # If the command was executed, change the mode
        if execute:

            if EditorMode.mode in [Modes.DELETE, Modes.YANK]:
                super().to_normal()

            elif EditorMode.mode == Modes.CHANGE:
                super().to_insert()

        return True


EDITOR_FILTERS = [
    NormalEventFilter,
    InsertEventFilter,
]
