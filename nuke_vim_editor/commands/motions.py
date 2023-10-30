from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..base_command import Command
from ..handler_parameters import HandlerParams


class MoveWordForward(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.NextWord, params.anchor)

        position = params.cursor.position()
        character = params.cursor.document().characterAt(position)
        if character in ['\u2029', '\n']:
            params.cursor.movePosition(QTextCursor.NextWord, params.anchor)

        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        return True


class MoveWordForwardEnd(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:

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
            if character in ['\u2029', '\n', ' ']:
                cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
                break

        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.EndOfLine, params.anchor)
        elif params.mode in ['VISUAL', 'YANK']:
            params.cursor.movePosition(QTextCursor.NextCharacter, params.anchor)
        return True

    def move_to_next_end_word(self, params: HandlerParams):
        params.cursor.movePosition(QTextCursor.NextWord, params.anchor)
        params.cursor.movePosition(QTextCursor.EndOfWord, params.anchor)
        params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)


class MoveWordBackward(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.PreviousWord, params.anchor)

        position = params.cursor.position()
        character = params.cursor.document().characterAt(position)
        if character in ['\u2029', '\n']:
            params.cursor.movePosition(QTextCursor.PreviousWord, params.anchor)

        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        return True


class MoveWordLeft(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Left, params.anchor)
        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        return True


class MoveWordRight(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Right, params.anchor)
        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        return True


class MoveLineUp(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Up, params.anchor)
        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        return True


class MoveLineDown(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.Down, params.anchor)
        if params.mode == 'VISUAL_LINE':
            params.cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        return True


class MoveLineStart(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.StartOfLine, params.anchor)
        return True


class MoveLineEnd(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.EndOfLine, params.anchor)
        if not params.visual:
            params.cursor.movePosition(QTextCursor.PreviousCharacter, params.anchor)
        return True


class MoveToStartOfBlock(Command):
    def __init__(self, editor: QPlainTextEdit, mode: str):
        self.editor = editor
        self.mode = mode

    def execute(self, params: HandlerParams) -> bool:
        params.cursor.movePosition(QTextCursor.StartOfLine, params.anchor)
        # Dont know if there is a better way to do this
        if params.cursor.block().text()[0] == ' ':
            params.cursor.movePosition(QTextCursor.NextWord, params.anchor)
        return True
