from __future__ import annotations
from enum import Enum, auto
from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Any, Callable, List, cast
from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
from PySide2.QtCore import QObject, QEvent, Qt


# TODO: Add options for arrow keys
# TODO: Add options for removing mouse
# TODO: Jump to line
# TODO: undo/redo
# TODO: Highlighting


class Modes(Enum):
    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()


class CurrentMode:
    mode = Modes.NORMAL


NormHandler = Callable[[QPlainTextEdit], Any]
_NORM_HANDLERS: List[NormHandler] = []


class BaseHandler(ABC):

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def to_insert_mode(self):
        CurrentMode.mode = Modes.INSERT
        # BUG: Cursor leaves a "ghost" cursor when switching modes
        self.editor.setCursorWidth(2)

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent) -> bool:
        return True

    @abstractmethod
    def handle(self, cursor: QTextCursor, event: QKeyEvent): ...


def register_handler(handler: NormHandler):
    _NORM_HANDLERS.append(handler)


@register_handler
class MovementHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_H:
            cursor.movePosition(QTextCursor.Left)
        elif key == Qt.Key_L:
            cursor.movePosition(QTextCursor.Right)
        elif key == Qt.Key_K:
            cursor.movePosition(QTextCursor.Up)
        elif key == Qt.Key_J:
            cursor.movePosition(QTextCursor.Down)
        elif key == Qt.Key_Dollar:
            cursor.movePosition(QTextCursor.EndOfLine)
        elif key == Qt.Key_0:
            cursor.movePosition(QTextCursor.StartOfLine)
        elif key == Qt.Key_AsciiCircum:
            cursor.movePosition(QTextCursor.StartOfLine)
            if cursor.block().text()[0] == " ":
                cursor.movePosition(QTextCursor.NextWord)
        elif key == Qt.Key_W:
            cursor.movePosition(QTextCursor.NextWord)
        elif key == Qt.Key_B:
            cursor.movePosition(QTextCursor.PreviousWord)
        elif key == Qt.Key_E:
            cursor.movePosition(QTextCursor.EndOfWord)


@register_handler
class DocumentHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        if modifiers == Qt.ShiftModifier and key == Qt.Key_G:
            cursor.movePosition(QTextCursor.End)

        # Paragraph down
        elif key == 125:
            document = self.editor.document()
            for i in range(cursor.blockNumber() + 1, document.lineCount() + 1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == "":
                    cursor.setPosition(current_line.position())
                    cursor.movePosition(QTextCursor.Up)
                    break

            cursor.movePosition(QTextCursor.NextBlock)

        # Paragraph up
        elif key == 123:

            document = self.editor.document()
            for i in range(cursor.blockNumber() - 1, -1, -1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == "":
                    cursor.setPosition(current_line.position())
                    cursor.movePosition(QTextCursor.Down)
                    break

            cursor.movePosition(QTextCursor.PreviousBlock)


@register_handler
class SearchHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Pound sign
        if key == 35:
            cursor.movePosition(QTextCursor.StartOfWord,
                                QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            word_under_cursor = cursor.selectedText()
            document = self.editor.document()
            current_line = cursor.blockNumber()
            match_found = False
            for i in range(current_line + 1, document.lineCount() + 1):

                line = document.findBlockByLineNumber(i)
                if word_under_cursor in line.text():
                    get_word_pos = line.text().find(word_under_cursor)
                    cursor.setPosition(line.position() + get_word_pos)
                    self.editor.setTextCursor(cursor)
                    match_found = True
                    break

            if not match_found:

                for i in range(0, current_line):

                    line = document.findBlockByLineNumber(i)
                    if word_under_cursor in line.text():
                        get_word_pos = line.text().find(word_under_cursor)
                        cursor.setPosition(line.position() + get_word_pos)
                        self.editor.setTextCursor(cursor)
                        break

        # Asterisk sign
        elif key == 42:
            cursor.movePosition(QTextCursor.StartOfWord,
                                QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            word_under_cursor = cursor.selectedText()
            document = self.editor.document()
            current_line = cursor.blockNumber()
            match_found = False
            for i in range(current_line - 1, -1, -1):

                line = document.findBlockByLineNumber(i)
                if word_under_cursor in line.text():
                    get_word_pos = line.text().find(word_under_cursor)
                    cursor.setPosition(line.position() + get_word_pos)
                    self.editor.setTextCursor(cursor)
                    match_found = True
                    break

            if not match_found:

                for i in range(document.lineCount() - 1, current_line, -1):

                    line = document.findBlockByLineNumber(i)
                    if word_under_cursor in line.text():
                        get_word_pos = line.text().find(word_under_cursor)
                        cursor.setPosition(line.position() + get_word_pos)
                        self.editor.setTextCursor(cursor)
                        break


@register_handler
class InsertHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):

        if CurrentMode.mode != Modes.NORMAL:
            return

        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_O and modifiers == Qt.ShiftModifier:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText("\n")
            cursor.movePosition(QTextCursor.Up)

        elif key == Qt.Key_I and modifiers == Qt.ShiftModifier:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.NextWord)

        elif key == Qt.Key_A and modifiers == Qt.ShiftModifier:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine)

        elif key == Qt.Key_I:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Right)

        elif key == Qt.Key_A:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Left)

        elif key == Qt.Key_O:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n")


@register_handler
class EditHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_C and modifiers == Qt.ShiftModifier:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        elif key == Qt.Key_X:
            cursor.deleteChar()
        elif key == Qt.Key_D and event.modifiers() == Qt.ShiftModifier:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()


@register_handler
class SomethingHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        print("something")

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent) -> bool:
        return False


class VimNormalMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()

        self._editor = editor
        self._handlers = [handler(self._editor) for handler in _NORM_HANDLERS]

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            return False

        if CurrentMode.mode == Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress:
            cursor = watched.textCursor()
            for handler in self._handlers:
                if handler.should_handle(cursor, cast(QKeyEvent, event)):
                    handler.handle(cursor, cast(QKeyEvent, event))
            watched.setTextCursor(cursor)
            return True

        return False


class VimInsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()
        self.editor = editor

    def eventFilter(self, watched: QObject, event):

        if CurrentMode.mode == Modes.NORMAL:
            return False

        if (
            event.type() == QEvent.KeyPress and
            (event.key() == Qt.Key_Escape and CurrentMode.mode == Modes.INSERT)
        ):
            # TODO: Cursor width should be width of character
            char_width = self.editor.fontMetrics().width(" ")
            self.editor.setCursorWidth(char_width)
            CurrentMode.mode = Modes.NORMAL
            return True
        return False


sampletext = '''
import random

def main(name):
    print(f"Hello {name}!")

for i in range(10):
    if i % 2 == 0:
        main("world")
    else:
        main("universe")
'''.lstrip()


def main():
    app = QApplication([])
    font = app.font()
    font.setFamilies(["JetBrainsMono Nerd Font", "Courier"])
    font.setPixelSize(30)
    app.setFont(font)

    window = QMainWindow()
    window.setGeometry(100, 100, 800, 600)
    editor = QPlainTextEdit()
    editor.setPlainText(sampletext)
    editor.setCursorWidth(18)
    window.setCentralWidget(editor)

    normal_mode = VimNormalMode(editor)
    editor.installEventFilter(normal_mode)

    insert_mode = VimInsertMode(editor)
    editor.installEventFilter(insert_mode)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
