from __future__ import annotations

from PySide2.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_normal_handler


@register_normal_handler
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
            # HACK: Dont know if there is a better way to do this
            if cursor.block().text()[0] == " ":
                cursor.movePosition(QTextCursor.NextWord)
        elif key == Qt.Key_W:
            cursor.movePosition(QTextCursor.NextWord)
        elif key == Qt.Key_B:
            cursor.movePosition(QTextCursor.PreviousWord)
        elif key == Qt.Key_E:
            cursor.movePosition(QTextCursor.EndOfWord)


@register_normal_handler
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


@register_normal_handler
class SearchHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def _find_word_in_line(self, cursor: QTextCursor, document: QTextDocument, line_number: int, word: str):
        line = document.findBlockByLineNumber(line_number)
        if word in line.text():
            get_word_pos = line.text().find(word)
            cursor.setPosition(line.position() + get_word_pos)
            self.editor.setTextCursor(cursor)
            return True
        return False

    def _find_word_in_document(self, cursor: QTextCursor, direction: str):
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)

        word_under_cursor = cursor.selectedText()
        document = self.editor.document()
        current_line = cursor.blockNumber()

        if direction == "up":
            line_range = range(current_line - 1, -1, -1)
            fallback_range = range(document.lineCount() - 1, current_line, -1)
        else:  # direction == "down"
            line_range = range(current_line + 1, document.lineCount() + 1)
            fallback_range = range(0, current_line)

        for i in line_range:
            if self._find_word_in_line(cursor, document, i, word_under_cursor):
                return True

        for i in fallback_range:
            if self._find_word_in_line(cursor, document, i, word_under_cursor):
                return True

        return False

    def _handle_39(self, cursor: QTextCursor):
        self._find_word_in_document(cursor, "up")

    # Usage for the second method
    def _handle_7(self, cursor: QTextCursor):
        self._find_word_in_document(cursor, "down")

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Pound sign
        if key == 35:
            self._handle_7(cursor)
        elif key == 42:
            self._handle_39(cursor)


@register_normal_handler
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


@register_normal_handler
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

        elif key == Qt.Key_S and modifiers == Qt.ShiftModifier:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        elif key == Qt.Key_S:
            super().to_insert_mode()
            cursor.deleteChar()

        elif key == Qt.Key_X:
            cursor.deleteChar()

        elif key == Qt.Key_D and event.modifiers() == Qt.ShiftModifier:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
