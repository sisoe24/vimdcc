from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..command import Command
from ..event_parameters import EventParams

# TODO: When Calling O, o commands, the cursor should keep the same column
# position. If the line is empty, the cursor should be placed at the first


def create_insert_command(move_position: QTextCursor.MoveOperation):
    class InsertCommand(Command):
        def __init__(self, editor: QPlainTextEdit, mode: str):
            self.editor = editor
            self.mode = mode

        def execute(self, params: EventParams):
            params.cursor.movePosition(move_position)
            return True

    return InsertCommand


class InsertO(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams):
        params.cursor.movePosition(QTextCursor.StartOfLine)
        params.cursor.insertText('\n')
        params.cursor.movePosition(QTextCursor.Up)
        return True


class Inserto(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams):
        params.cursor.movePosition(QTextCursor.EndOfLine)
        params.cursor.insertText('\n')
        return True


Inserti = create_insert_command(QTextCursor.Left)
InsertI = create_insert_command(QTextCursor.StartOfLine)
Inserta = create_insert_command(QTextCursor.Right)
InsertA = create_insert_command(QTextCursor.EndOfLine)
