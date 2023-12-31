from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import MoveCommand
from ..handler_parameters import HandlerParams


class MoveDocumentUp(MoveCommand):
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Start, params.anchor)
        return True


class MoveDocumentDown(MoveCommand):
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.End, params.anchor)
        if not params.visual:
            params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
        return True


class MoveParagraphUp(MoveCommand):
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def _do_execute(self, params: HandlerParams) -> bool:
        cursor = params.cursor
        document = self.editor.document()
        paragraphs_left = False

        for i in range(cursor.blockNumber() - 1, -1, -1):
            current_line = document.findBlockByLineNumber(i)
            if current_line.text() == '':
                paragraphs_left = True
                cursor.setPosition(current_line.position(), params.anchor)
                break

        if not paragraphs_left:
            cursor.movePosition(QTextCursor.Start, params.anchor)

        return True


class MoveParagraphDown(MoveCommand):
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def _do_execute(self, params: HandlerParams) -> bool:
        cursor = params.cursor
        document = self.editor.document()

        paragraphs_left = False
        for i in range(cursor.blockNumber() + 1, document.lineCount()):
            current_line = document.findBlockByLineNumber(i)
            if current_line.text() == '':
                cursor.setPosition(current_line.position(), params.anchor)
                paragraphs_left = True
                break

        if not paragraphs_left:
            cursor.movePosition(QTextCursor.End, params.anchor)
            if not params.visual:
                cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)

        return True
