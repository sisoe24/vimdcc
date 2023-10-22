from __future__ import annotations

import re
from typing import Dict

from PySide2.QtGui import QTextCursor, QTextDocument
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..marks import Marks
from .._types import EventParams
from ..commands import Command
from ..registers import Registers
from ..handlers_core import BaseHandler, register_normal_handler
from ..commands.motions import (MoveLineUp, MoveLineEnd, MoveLineDown,
                                MoveWordLeft, MoveLineStart, MoveWordRight,
                                MoveWordForward, MoveWordBackward,
                                MoveToStartOfBlock, MoveWordForwardEnd)


@register_normal_handler
class MotionHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.command_map: Dict[str, Command] = {
            'w': MoveWordForward(editor, 'NORMAL'),
            'b': MoveWordBackward(editor, 'NORMAL'),
            'e': MoveWordForwardEnd(editor, 'NORMAL'),
            # 'W': self.move_word_forward,
            # 'B': self.move_word_backward,
            # 'E': self.move_word_forward,
            'h': MoveWordLeft(editor, 'NORMAL'),
            'l': MoveWordRight(editor, 'NORMAL'),
            'k': MoveLineUp(editor, 'NORMAL'),
            'j': MoveLineDown(editor, 'NORMAL'),
            '$': MoveLineEnd(editor, 'NORMAL'),
            '0': MoveLineStart(editor, 'NORMAL'),
            '^': MoveToStartOfBlock(editor, 'NORMAL'),
        }

    def handle(self, params: EventParams):
        command = self.command_map.get(params.keys)
        return command.execute(params) if command else False


@register_normal_handler
class DocumentHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        key_sequence = params.keys
        modifiers = params.modifiers
        cursor = params.cursor

        select = (
            QTextCursor.KeepAnchor
            if params.visual
            else QTextCursor.MoveAnchor
        )

        if key_sequence == 'G':
            cursor.movePosition(QTextCursor.End, select)
            return True

        if key_sequence == 'gg':
            cursor.movePosition(QTextCursor.Start, select)
            return True

        if key_sequence == '}':
            document = self.editor.document()
            for i in range(cursor.blockNumber() + 1, document.lineCount() + 1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == '':
                    cursor.setPosition(current_line.position(), select)
                    cursor.movePosition(QTextCursor.Up, select)
                    break

            cursor.movePosition(QTextCursor.NextBlock, select)

            return True

        if key_sequence == '{':
            document = self.editor.document()
            for i in range(cursor.blockNumber() - 1, -1, -1):
                current_line = document.findBlockByLineNumber(i)
                if current_line.text() == '':
                    cursor.setPosition(current_line.position(), select)
                    cursor.movePosition(QTextCursor.Down, select)
                    break

            cursor.movePosition(QTextCursor.PreviousBlock, select)
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

        if direction == 'up':
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

    def handle(self, params: EventParams):

        key_sequence = params.keys
        modifiers = params.modifiers
        cursor = params.cursor

        if key_sequence == '#':
            self._find_word_in_document(cursor, 'up')
            return True

        if key_sequence == '*':
            self._find_word_in_document(cursor, 'down')
            return True

        if key_sequence.startswith('f') and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'forward', stop_before=False)

        if key_sequence.startswith('F') and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'backward', stop_before=False)

        if key_sequence.startswith('t') and len(key_sequence) == 2:
            return self.move_cursor(key_sequence, cursor, 'forward', stop_before=True)

        if key_sequence.startswith('T') and len(key_sequence) == 2:
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

    def handle(self, params: EventParams):

        key_sequence = params.keys
        modifiers = params.modifiers
        cursor = params.cursor

        if key_sequence == 'O' and 'shift' in modifiers:
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText('\n')
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

        if key_sequence == 'i':
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Right)
            return True

        if key_sequence == 'a':
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.Left)
            return True

        if key_sequence == 'o':
            super().to_insert_mode()
            cursor.movePosition(QTextCursor.EndOfLine)
            start = cursor.position()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down)
            start_line_pos = cursor.position()
            cursor.movePosition(QTextCursor.NextWord)
            next_word_pos = cursor.position()
            spaces = next_word_pos - start_line_pos
            cursor.setPosition(start)
            cursor.insertText('\n' + ' ' * spaces)
            return True

        return False


@register_normal_handler
class MarksHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        key_sequence = params.keys
        cursor = params.cursor

        if key_sequence.startswith('m') and len(key_sequence) == 2:
            Marks.add(
                key_sequence[1], {
                    'text': cursor.block().text(),
                    'position': cursor.position()
                }
            )
            return True

        if key_sequence.startswith('`') and len(key_sequence) == 2:

            mark = Marks.get(key_sequence[1])
            if mark is None:
                return True

            cursor.setPosition(mark['position'])
            return True

        return False


@register_normal_handler
class YankHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        key_sequence = params.keys
        cursor = params.cursor
        mode = params.mode

        if key_sequence == 'y' and mode in ['VISUAL', 'VISUAL_LINE']:
            Registers.add(cursor.selectedText())
            cursor.clearSelection()
            return True

        if key_sequence == 'yw':
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            Registers.add(cursor.selectedText())
            cursor.clearSelection()
            return True

        if key_sequence == 'yy':
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            Registers.add(cursor.selectedText())
            cursor.clearSelection()
            return True

        return False


@register_normal_handler
class VisualEditHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.command_map = {
            'c': self.cut_text,
            'd': self.delete_text,
        }

    def handle(self, params: EventParams):
        if not params.visual:
            return False

        command = self.command_map.get(params.keys)
        return command(params) if command else False

    def delete_text(self, params: EventParams) -> bool:
        params.cursor.removeSelectedText()
        super().to_normal_mode()
        return True

    def cut_text(self, params: EventParams) -> bool:
        params.cursor.removeSelectedText()
        super().to_insert_mode()
        return True


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

    def handle(self, params: EventParams):

        key_sequence = params.keys
        modifiers = params.modifiers
        cursor = params.cursor

        select = (
            QTextCursor.KeepAnchor
            if params.visual
            else QTextCursor.MoveAnchor
        )

        if key_sequence == 'dd':
            self._delete_line(cursor)
            return True

        if key_sequence == 'dw':
            self._delete_word(cursor)
            return True

        if key_sequence == 'cc' or key_sequence == 'S' and 'shift' in modifiers:
            super().to_insert_mode()
            self._delete_line(cursor)
            return True

        if key_sequence == 'cw':
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

        if key_sequence == 'J':
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(' ')
            return True

        if key_sequence.startswith('r') and len(key_sequence) == 2:
            cursor.movePosition(QTextCursor.NextCharacter)
            cursor.deletePreviousChar()
            cursor.insertText(key_sequence[1])
            return True

        count = re.search(r'd(\d+)\w', key_sequence)
        if count:
            for _ in range(int(count[1])):
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
            return True

        return False


@register_normal_handler
class SwapCaseHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        key_sequence = params.keys
        mode = params.mode
        cursor = params.cursor

        if key_sequence == 'gu' and mode in ['VISUAL', 'VISUAL_LINE']:
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(text.lower())
            super().to_normal_mode()
            return True

        if key_sequence == 'gU':
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(text.upper())
            super().to_normal_mode()
            return True

        if key_sequence in ['g~', '~']:
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(text.swapcase())
            super().to_normal_mode()

            return True

        return False


@register_normal_handler
class MissingHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):
        key_sequence = params.keys
        mode = params.mode
        cursor = params.cursor

        if key_sequence == 'R':
            print('TODO: Redo Mode')
            return True

        if key_sequence == '<<':
            print('TODO: << (Shift Left)')
            return True

        if key_sequence == '>>':
            print('TODO: >> (Shift Right)')
            return True

        return False