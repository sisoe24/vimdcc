from __future__ import annotations

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_handler


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
