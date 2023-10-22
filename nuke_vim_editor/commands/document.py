from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from .._types import EventParams
from ..commands_core import Command


class MoveDocumentUp(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        params.cursor.movePosition(QTextCursor.Start, params.anchor)
        return True


class MoveDocumentDown(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        params.cursor.movePosition(QTextCursor.End, params.anchor)
        if not params.visual:
            params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
        return True


class MoveParagraphUp(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
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


class MoveParagraphDown(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
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
