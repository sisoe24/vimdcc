from __future__ import annotations

import re
from typing import Dict

from PySide2.QtGui import QTextCursor, QTextDocument
from PySide2.QtWidgets import QPlainTextEdit

from ..command import Command
from ..handlers_core import BaseHandler, register_normal_handler
from ..commands.insert import (Inserta, InsertA, Inserti, InsertI, InsertO,
                               Inserto)
from ..commands.motions import (MoveLineUp, MoveLineEnd, MoveLineDown,
                                MoveWordLeft, MoveLineStart, MoveWordRight,
                                MoveWordForward, MoveWordBackward,
                                MoveToStartOfBlock, MoveWordForwardEnd)
from ..event_parameters import EventParams
from ..commands.document import (MoveDocumentUp, MoveParagraphUp,
                                 MoveDocumentDown, MoveParagraphDown)
from ..commands.swap_case import SwapCase, SwapLower, SwapUpper


@register_normal_handler
class MotionHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, Command] = {
            'w': MoveWordForward(editor, 'NORMAL'),
            'b': MoveWordBackward(editor, 'NORMAL'),
            'e': MoveWordForwardEnd(editor, 'NORMAL'),
            'h': MoveWordLeft(editor, 'NORMAL'),
            'l': MoveWordRight(editor, 'NORMAL'),
            'k': MoveLineUp(editor, 'NORMAL'),
            'j': MoveLineDown(editor, 'NORMAL'),
            '$': MoveLineEnd(editor, 'NORMAL'),
            '0': MoveLineStart(editor, 'NORMAL'),
            '^': MoveToStartOfBlock(editor, 'NORMAL'),
        }

    def handle(self, params: EventParams):
        command = self.commands.get(params.keys)
        return command.execute(params) if command else False


@register_normal_handler
class DocumentHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, Command] = {
            'G': MoveDocumentDown(editor, 'NORMAL'),
            'gg': MoveDocumentUp(editor, 'NORMAL'),
            '{': MoveParagraphUp(editor, 'NORMAL'),
            '}': MoveParagraphDown(editor, 'NORMAL'),
        }

    def handle(self, params: EventParams):
        command = self.commands.get(params.keys)
        return command.execute(params) if command else False


@register_normal_handler
class InsertHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, Command] = {
            'i': Inserti(editor, 'NORMAL'),
            'I': InsertI(editor, 'NORMAL'),
            'a': Inserta(editor, 'NORMAL'),
            'A': InsertA(editor, 'NORMAL'),
            'o': Inserto(editor, 'NORMAL'),
            'O': InsertO(editor, 'NORMAL'),
        }

    def handle(self, params: EventParams):
        command = self.commands.get(params.keys)
        if command and command.execute(params):
            super().to_insert_mode()
            return True
        return False


@register_normal_handler
class SwapCaseHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, Command] = {
            '~': SwapCase(editor, 'NORMAL'),
            'g~': SwapCase(editor, 'NORMAL'),
            'gu': SwapLower(editor, 'NORMAL'),
            'gU': SwapUpper(editor, 'NORMAL'),
        }

    def handle(self, params: EventParams):
        command = self.commands.get(params.keys)
        if command and command.execute(params):
            super().to_normal_mode()
            return True
        return False


@register_normal_handler
class MarksHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def set_mark(self, key: str, params: EventParams):
        self.registers.update('marks', key, params.cursor.position())
        return True

    def move_to_mark(self, key: str, params: EventParams):
        pos = self.registers.get('marks', key)
        if pos:
            params.cursor.setPosition(pos)
        else:
            params.status_bar.emit('NORMAL', f'{key} mark not set')

        return True

    def handle(self, params: EventParams):
        key_sequence = params.keys

        if key_sequence.startswith('m') and len(key_sequence) == 2:
            return self.set_mark(key_sequence[1], params)

        if key_sequence.startswith('`') and len(key_sequence) == 2:
            return self.move_to_mark(key_sequence[1], params)

        return False


@register_normal_handler
class YankHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def _add_to_register(self, register, cursor: QTextCursor):
        self.registers[register][self.named] = cursor.selectedText()
        cursor.clearSelection()

    def yank_line(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.registers.update('named', '0', cursor.selectedText())
        return True

    def handle(self, params: EventParams):

        key_sequence = params.keys
        cursor = params.cursor
        mode = params.mode

        print('➡ key_sequence :', key_sequence)
        if key_sequence == 'y':
            if mode not in ['VISUAL', 'VISUAL_LINE', 'YANK']:
                print('yank line')
                return self.yank_line(cursor)

            self.registers.update('named', '0', cursor.blockNumber())
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
