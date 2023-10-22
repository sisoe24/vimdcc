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
        return True


class MoveParagraphUp(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        cursor = params.cursor
        document = self.editor.document()
        for i in range(cursor.blockNumber() - 1, -1, -1):
            current_line = document.findBlockByLineNumber(i)
            if current_line.text() == '':
                cursor.setPosition(current_line.position(), params.anchor)
                cursor.movePosition(QTextCursor.Down, params.anchor)
                break

        cursor.movePosition(QTextCursor.PreviousBlock, params.anchor)
        return True


class MoveParagraphDown(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        cursor = params.cursor
        document = self.editor.document()
        for i in range(cursor.blockNumber() + 1, document.lineCount() + 1):
            current_line = document.findBlockByLineNumber(i)
            if current_line.text() == '':
                cursor.setPosition(current_line.position(), params.anchor)
                cursor.movePosition(QTextCursor.Up, params.anchor)
                break

        cursor.movePosition(QTextCursor.NextBlock, params.anchor)

        return True
