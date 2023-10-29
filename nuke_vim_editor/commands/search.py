from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..base_command import Command
from ..handler_parameters import EventParams


class SearchForward(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        print('SearchForward')
        return True


class SearchBackward(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        print('SearchBackward')
        return True


class SearchNext(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        print('SearchNext')
        return True


class SearchPrevious(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        print('SearchPrevious')
        return True


class SearchUnderCursor(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: EventParams) -> bool:
        print('SearchUnderCursor')
        return True
