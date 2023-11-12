from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import BaseCommand, MoveCommand
from ..handler_parameters import HandlerParams


class MoveWordForward(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.NextWord, params.anchor)

        position = params.cursor.position()
        character = params.cursor.document().characterAt(position)
        if character in ['\u2029', '\n']:
            params.cursor.movePosition(QTextCursor.NextWord, params.anchor)

        return True


class MoveWordForwardEnd(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def move_to_next_end_word(self, params: HandlerParams):
        params.cursor.movePosition(QTextCursor.NextWord, params.anchor)
        params.cursor.movePosition(QTextCursor.EndOfWord, params.anchor)
        params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)

    def _do_execute(self, params: HandlerParams) -> bool:
        # BUG: e motion This is not working properly

        cursor = params.cursor
        has_seen_alnum = False

        while cursor.movePosition(QTextCursor.NextCharacter, params.anchor):
            position = cursor.position()
            character = cursor.document().characterAt(position)

            if character.isalnum():
                has_seen_alnum = True

            if not has_seen_alnum:
                self.move_to_next_end_word(params)
                break

            # this check is only for the first word
            if character.isspace():
                cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
                break

        if params.mode in ['VISUAL', 'YANK', 'DELETE', 'CHANGE']:
            params.cursor.movePosition(QTextCursor.NextCharacter, params.anchor)

        return True


class MoveWordBackward(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.PreviousWord, params.anchor)

        position = params.cursor.position()
        character = params.cursor.document().characterAt(position)
        if character.isspace():
            params.cursor.movePosition(QTextCursor.PreviousWord, params.anchor)

        return True


class MoveWordLeft(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Left, params.anchor)
        return True


class MoveWordRight(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Right, params.anchor)
        return True


class MoveLineUp(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        if params.mode in ['YANK', 'DELETE', 'CHANGE']:
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            params.cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        params.cursor.movePosition(QTextCursor.Up, params.anchor)
        return True


class MoveLineDown(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        if params.mode in ['YANK', 'DELETE', 'CHANGE']:
            params.cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        params.cursor.movePosition(QTextCursor.Down, params.anchor)
        return True


class MoveLineStart(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.StartOfLine, params.anchor)
        return True


class MoveLineEnd(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.EndOfLine, params.anchor)
        if not params.visual:
            params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
        return True


class MoveToStartOfBlock(MoveCommand):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def _do_execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.StartOfLine, params.anchor)
        # Dont know if there is a better way to do this
        if params.cursor.block().text()[0] == ' ':
            params.cursor.movePosition(QTextCursor.NextWord, params.anchor)
        return True
