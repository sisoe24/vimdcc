from __future__ import annotations
import re
from typing import List

from PySide2.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_normal_handler


@register_normal_handler
class MovementHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == "w":
            cursor.movePosition(QTextCursor.NextWord)
            return True

        if key_sequence == "h":
            cursor.movePosition(QTextCursor.Left)
            return True

        if key_sequence == "l":
            cursor.movePosition(QTextCursor.Right)
            return True

        if key_sequence == "k":
            cursor.movePosition(QTextCursor.Up)
            return True

        if key_sequence == "j":
            cursor.movePosition(QTextCursor.Down)
            return True

        if key_sequence == "$":
            cursor.movePosition(QTextCursor.EndOfLine)
            return True

        if key_sequence == "0":
            cursor.movePosition(QTextCursor.StartOfLine)
            return True

        if key_sequence == "^":
            cursor.movePosition(QTextCursor.StartOfLine)
            # HACK: Dont know if there is a better way to do this
            if cursor.block().text()[0] == " ":
                cursor.movePosition(QTextCursor.NextWord)
                return True

        if key_sequence == "w":
            cursor.movePosition(QTextCursor.NextWord)
            return True

        if key_sequence == "b":
            cursor.movePosition(QTextCursor.PreviousWord)
            return True

        if key_sequence == "e":
            cursor.movePosition(QTextCursor.EndOfWord)

        return False


@register_normal_handler
class DocumentHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == 'G' and 'shift' in modifiers:
            cursor.movePosition(QTextCursor.End)
            return True

        if key_sequence == "gg":
            cursor.movePosition(QTextCursor.Start)
            return True

        if key_sequence == "}":
            document = self.editor.document()
            for i in range(cursor.blockNumber() + 1, document.lineCount() + 1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == "":
                    cursor.setPosition(current_line.position())
                    cursor.movePosition(QTextCursor.Up)
                    break

            cursor.movePosition(QTextCursor.NextBlock)

            return True

        if key_sequence == "{":
            document = self.editor.document()
            for i in range(cursor.blockNumber() - 1, -1, -1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == "":
                    cursor.setPosition(current_line.position())
                    cursor.movePosition(QTextCursor.Down)
                    break

            cursor.movePosition(QTextCursor.PreviousBlock)
            return True

        return False


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

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == '#':
            self._handle_7(cursor)
            return True

        if key_sequence == "*":
            self._handle_39(cursor)
            return True

        return False


@register_normal_handler
class InsertHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == 'O' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText("\n")
            cursor.movePosition(QTextCursor.Up)
            return True

        if key_sequence == 'I' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.NextWord)
            return True

        if key_sequence == 'A' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine)
            return True

        if key_sequence == "i":
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Right)
            return True

        if key_sequence == "a":
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Left)
            return True

        if key_sequence == "o":
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n")
            return True

        return False


@register_normal_handler
class EditHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):


        if key_sequence == "dd":
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        if key_sequence == "dw":
            cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        count = re.search(r'\w(\d+)\w', key_sequence)
        if count:
            for _ in range(int(count[1])):
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
            return True

        if key_sequence == "cc":
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        if key_sequence == "cw":
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        if key_sequence == 'C' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        if key_sequence == 'S' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        if key_sequence == 's':
            super().to_insert_mode()
            cursor.deleteChar()
            return True

        if key_sequence == 'x':
            cursor.deleteChar()
            return True
        
        if key_sequence == 'D' and 'shift' in modifiers:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True

        return False
