from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_visual_line_handler
from ..event_parameters import EventParams


@register_visual_line_handler
class VisualLineHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        key = params.keys
        cursor = params.cursor

        if key == 'j':
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            return True

        if key == 'k':
            cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            return True

        if key == 'h':
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            return True

        if key == 'l':
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

        if key == 'd':
            self.editor.cut()
            return True

        if key == 'y':
            cursor = params.cursor
            cursor.select(QTextCursor.LineUnderCursor)
            self.editor.copy()
            cursor.clearSelection()
            return True

        return False
