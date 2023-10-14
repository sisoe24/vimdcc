from __future__ import annotations

import re
from typing import Dict, List

from PySide2.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..marks import Marks
from ..registers import Registers
from ..handlers_core import BaseHandler, register_normal_handler
from .._types import Modes


@register_normal_handler
class MovementHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        key = event.key()

        select = (
            QTextCursor.MoveAnchor
            if self.editor_state() == Modes.NORMAL
            else QTextCursor.KeepAnchor
        )
        print("➡ select :", select)

        if key_sequence == "w":
            cursor.movePosition(QTextCursor.NextWord, select)
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
            # Dont know if there is a better way to do this
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
    last_match = None

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.last_search_char = None
        self.last_search_direction = None
        self.last_search_stop_before = None
        self.last_word_under_cursor = None

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
        self.last_word_under_cursor = word_under_cursor
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

    def move_cursor(self, key_sequence, cursor, direction='forward', stop_before=False):
        if len(key_sequence) == 2:
            target_char = key_sequence[1]
            cursor_position = cursor.position()
            block_position = cursor.block().position()

            # Calculate the relative cursor position within the current line
            relative_cursor_position = cursor_position - block_position

            # Get the text of the current line
            current_line = cursor.block().text()

            if direction == 'forward':
                # Only consider the part of the line after the cursor
                line_to_search = current_line[relative_cursor_position + 1:]
                find_result = line_to_search.find(target_char)
            else:
                # Only consider the part of the line before the cursor
                line_to_search = current_line[:relative_cursor_position]
                find_result = line_to_search.rfind(target_char)

            if find_result == -1:
                return False

            # Calculate the new cursor position in the context of the entire document
            if direction == 'forward':
                new_cursor_position = block_position + relative_cursor_position + 1 + find_result
            else:
                new_cursor_position = block_position + find_result

            if stop_before and direction == 'forward':
                new_cursor_position -= 1
            elif stop_before and direction == 'backward':
                new_cursor_position += 1

            self.last_search_char = target_char
            self.last_search_direction = direction
            self.last_search_stop_before = stop_before

            cursor.setPosition(new_cursor_position)
            return True
        return False

    def repeat_last_search(self, cursor, reverse=False):
        if self.last_search_char is None:
            return False  # No previous search to repeat

        direction = self.last_search_direction
        if reverse:
            direction = 'backward' if direction == 'forward' else 'forward'

        key_sequence = ' ' + self.last_search_char  # Placeholder for the first character
        return self.move_cursor(key_sequence, cursor, direction, self.last_search_stop_before)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == '#':
            self._find_word_in_document(cursor, "up")
            return True

        if key_sequence == "*":
            self._find_word_in_document(cursor, "down")
            return True

        if key_sequence.startswith("f") and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'forward', stop_before=False)

        if key_sequence.startswith("F") and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'backward', stop_before=False)

        if key_sequence.startswith("t") and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'forward', stop_before=True)

        if key_sequence.startswith("T") and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'backward', stop_before=True)

        if key_sequence == ';':
            self.repeat_last_search(cursor, reverse=False)
            return True

        if key_sequence == ',':
            self.repeat_last_search(cursor, reverse=True)
            return True

        if key_sequence == 'n':
            print(self.last_word_under_cursor)
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
class MarksHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence.startswith('m') and len(key_sequence) == 2:
            Marks.add(
                key_sequence[1], {
                    "text": cursor.block().text(),
                    "position": cursor.position()
                }
            )
            return True

        if key_sequence.startswith('`') and len(key_sequence) == 2:

            mark = Marks.get(key_sequence[1])
            if mark is None:
                return True

            cursor.setPosition(mark["position"])
            return True

        return False


@register_normal_handler
class YankHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == 'yy':
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            Registers.add(cursor.selectedText())
            return True

        return False


@register_normal_handler
class EditHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def _delete_line(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

    def _delete_word(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

    def _delete_from_cursor(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):

        if key_sequence == "dd":
            self._delete_line(cursor)
            return True

        if key_sequence == "dw":
            self._delete_word(cursor)
            return True

        if key_sequence == "cc" or key_sequence == "S" and 'shift' in modifiers:
            super().to_insert_mode()
            self._delete_line(cursor)
            return True

        if key_sequence == "cw":
            super().to_insert_mode()
            self._delete_word(cursor)
            return True

        if key_sequence == 'C' and 'shift' in modifiers:
            super().to_insert_mode()
            self._delete_from_cursor(cursor)
            return True

        if key_sequence == 'D' and 'shift' in modifiers:
            self._delete_from_cursor(cursor)
            return True

        if key_sequence == 's':
            super().to_insert_mode()
            cursor.deleteChar()
            return True

        if key_sequence == 'x':
            cursor.deleteChar()
            return True

        count = re.search(r'\w(\d+)\w', key_sequence)
        if count:
            for _ in range(int(count[1])):
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
            return True

        return False

# lorem ipsum dolor sit amet consectetur adipiscing

# incididunt ut labore et dolore magna aliqua
# esto es una prueba manzanita


def main(name): print(f'Hello {name}!')
