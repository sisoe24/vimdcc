from typing import List, Union, Literal, Optional, cast

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtCore import Qt, QEvent, QObject
from PySide2.QtWidgets import QPlainTextEdit

from .logger import LOGGER
from .status_bar import status_bar
from .editor_state import Modes, EditorMode
from .handler_base import HandlerType, get_normal_handlers
from .handler_parameters import HandlerParams

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


class BaseFilter(QObject):
    key_sequence = ''

    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor

    def to_normal(self):
        status_bar.emit('NORMAL', '')
        self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
        EditorMode.mode = Modes.NORMAL
        self.key_sequence = ''
        return True

    def to_insert(self):
        status_bar.emit('INSERT', '')
        self.editor.setCursorWidth(1)
        EditorMode.mode = Modes.INSERT
        self.key_sequence = ''
        return True

    def to_mode(self, mode: Modes, keys: str = ''):
        status_bar.emit(mode.value, keys)
        EditorMode.mode = mode
        self.key_sequence = ''
        return True


class InsertEventFilter(QObject):
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


class NormalEventFilter(BaseFilter):

    operators = Literal['d', 'c', 'y', 'v']
    text_objects = ['i', 'a']

    def __init__(self, editor: QPlainTextEdit, handlers: Optional[List[HandlerType]] = None, parent=None):
        super().__init__(parent)
        LOGGER.debug('Initializing normal mode')

        self.editor = editor
        LOGGER.debug(f'editor: {editor}')

        handlers = handlers or get_normal_handlers()
        self._handlers = [handler(self.editor) for handler in handlers]
        LOGGER.debug(f'handlers: {self._handlers}')

    def _check_edit_mode(self, operator: operators):
        """Check if the key sequence is a edit mode.

        This is an ugly hack to check if the key sequence is a edit mode. If a
        double key is pressed, like 'd' and 'w', the first key is the edit mode
        while the second is the command. It then sets the edit mode and removes
        the first key from the sequence and passes the second key to the handlers
        to be executed.

        """
        if (
            len(self.key_sequence) == 2
            and self.key_sequence[0] == operator
            and self.key_sequence[1] not in [*self.text_objects, operator]
        ):
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

    def eventFilter(self, watched: QObject, event: QEvent):

        if not isinstance(watched, QPlainTextEdit):
            assert False, 'This event filter should only be installed on a QPlainTextEdit'

        if EditorMode.mode not in [Modes.NORMAL, Modes.VISUAL,
                                   Modes.VISUAL_LINE, Modes.YANK,
                                   Modes.DELETE, Modes.CHANGE]:
            return False

        if event.type() == QEvent.KeyPress:
            return self.parse_keys(watched, event)
        return False

    def parse_keys(self, editor: QPlainTextEdit, event: QEvent):

        cursor = editor.textCursor()
        key_event = cast(QKeyEvent, event)
        modifiers = extract_modifiers(key_event.modifiers())

        self.key_sequence += key_event.text().strip()
        status_bar.emit('NORMAL', self.key_sequence)

        self._check_edit_mode('d')
        self._check_edit_mode('c')
        self._check_edit_mode('v')
        self._check_edit_mode('y')

        if key_event.key() == Qt.Key_Escape:
            super().to_mode(Modes.NORMAL, '')
            cursor.clearSelection()
            self.editor.setTextCursor(cursor)
            return True

        if key_event.key() == Qt.Key_Backspace:
            self.key_sequence = self.key_sequence[:-1]
            return True

        if self.key_sequence == 'V':
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            return super().to_mode(Modes.VISUAL_LINE)

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
                status_bar.emit('NORMAL', '')
                execute = True
                break

        if execute and EditorMode.mode in [Modes.DELETE, Modes.YANK]:
            super().to_normal()
            return True

        if execute and EditorMode.mode == Modes.CHANGE:
            super().to_insert()
            return True

        return True


EDITOR_MODES = [
    NormalEventFilter,
    InsertEventFilter,
]
