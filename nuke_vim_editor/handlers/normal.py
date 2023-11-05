from __future__ import annotations

import re
from typing import Dict, Optional

from PySide2.QtGui import QTextCursor
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import Command
from ..handler_base import BaseHandler, register_normal_handler
from ..commands.insert import (Inserta, InsertA, Inserti, InsertI, InsertO,
                               Inserto)
from ..commands.search import SearchCommand
from ..commands.motions import (MoveLineUp, MoveLineEnd, MoveLineDown,
                                MoveWordLeft, MoveLineStart, MoveWordRight,
                                MoveWordForward, MoveWordBackward,
                                MoveToStartOfBlock, MoveWordForwardEnd)
from ..commands.document import (MoveDocumentUp, MoveParagraphUp,
                                 MoveDocumentDown, MoveParagraphDown)
from ..commands.swap_case import SwapCase, SwapLower, SwapUpper
from ..handler_parameters import HandlerParams


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

    def handle(self, params: HandlerParams):
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

    def handle(self, params: HandlerParams):
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

    def handle(self, params: HandlerParams):
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

    def handle(self, params: HandlerParams):
        command = self.commands.get(params.keys)
        if command and command.execute(params):
            super().to_normal_mode()
            return True
        return False


@register_normal_handler
class MarksHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def set_mark(self, key: str, params: HandlerParams):
        self.registers.update('marks', key, params.cursor.position())
        return True

    def move_to_mark(self, key: str, params: HandlerParams):
        pos = self.registers.get('marks', key)
        if pos:
            params.cursor.setPosition(pos)
        else:
            params.status_bar.emit('NORMAL', f'{key} mark not set')

        return True

    def handle(self, params: HandlerParams):
        key_sequence = params.keys

        if key_sequence.startswith('m') and len(key_sequence) == 2:
            return self.set_mark(key_sequence[1], params)

        if key_sequence.startswith('`') and len(key_sequence) == 2:
            return self.move_to_mark(key_sequence[1], params)

        return False


@register_normal_handler
class SearchHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands = {
            'n': self.go_down,
            'N': self.go_up,
            '*': self.search_down_under_cursor,
            '#': self.search_up_under_cursor,
        }
        self.search = SearchCommand(editor)

    def handle(self, params: HandlerParams) -> bool:
        key = params.event.key()
        key_sequence = params.keys

        if key_sequence.startswith('?') and key == 16777220:
            return self.search_word_up(params, key_sequence[1:])

        if key_sequence.startswith('/') and key == 16777220:
            return self.search_word_down(params, key_sequence[1:])

        command = self.commands.get(params.keys)
        return command(params) if command else False

    def get_word_under_cursor(self, cursor: QTextCursor) -> str:
        initial_position = cursor.position()
        cursor.select(QTextCursor.WordUnderCursor)
        text = cursor.selectedText()
        cursor.setPosition(initial_position)
        return text

    def _search_down(self, params: HandlerParams, key: str):
        self.search.find(key)
        return self.go_down(params)

    def _search_up(self, params: HandlerParams, key: str):
        self.search.find(key)
        return self.go_up(params)

    def search_down_under_cursor(self, params: HandlerParams):
        return self._search_down(params, self.get_word_under_cursor(params.cursor))

    def search_up_under_cursor(self, params: HandlerParams):
        return self._search_up(params, self.get_word_under_cursor(params.cursor))

    def search_word_up(self, params: HandlerParams, key: str):
        return self._search_up(params, key)

    def search_word_down(self, params: HandlerParams, key: str):
        return self._search_down(params, key)

    def go_up(self, params: HandlerParams):
        pos = self.search.find_next_up(params.cursor.position())
        if pos is not None:
            params.cursor.setPosition(pos)
        return True

    def go_down(self, params: HandlerParams):
        pos = self.search.find_next_down(params.cursor.position())
        if pos is not None:
            params.cursor.setPosition(pos)
        return True


@register_normal_handler
class SearchLineHandler(BaseHandler):

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.search = SearchCommand(editor)
        self.commands = {
            ';': self.search_forward_again,
            ',': self.search_backward_again,
        }

    def _set_cursor(self, cursor: QTextCursor, pos: Optional[int]):
        if pos is None:
            return False
        cursor.setPosition(pos)
        return True

    def search_forward(self, params: HandlerParams, key: str):
        self.search.find(key)
        cursor = params.cursor
        pos = self.search.find_next_down(cursor.position())
        return self._set_cursor(cursor, pos)

    def search_backward(self, params: HandlerParams, key: str):
        self.search.find(key)
        cursor = params.cursor
        pos = self.search.find_next_up(cursor.position())
        return self._set_cursor(cursor, pos)

    def search_forward_before(self, params: HandlerParams, key: str):
        if not self.search_forward(params, key):
            return False
        params.cursor.movePosition(QTextCursor.PreviousCharacter)
        return True

    def search_backward_before(self, params: HandlerParams, key: str):
        if not self.search_backward(params, key):
            return False
        params.cursor.movePosition(QTextCursor.NextCharacter)
        return True

    def search_forward_again(self, params: HandlerParams):
        pos = self.search.find_next_down(params.cursor.position())
        return self._set_cursor(params.cursor, pos)

    def search_backward_again(self, params: HandlerParams):
        pos = self.search.find_next_up(params.cursor.position())
        return self._set_cursor(params.cursor, pos)

    def handle(self, params: HandlerParams):
        keys = params.keys

        if keys.startswith('f') and len(keys) == 2:
            self.search_forward(params, keys[1])
            return True

        if keys.startswith('t') and len(keys) == 2:
            self.search_forward_before(params, keys[1])
            return True

        if keys.startswith('F') and len(keys) == 2:
            self.search_backward(params, keys[1])
            return True

        if keys.startswith('T') and len(keys) == 2:
            self.search_backward_before(params, keys[1])
            return True

        commands = self.commands.get(keys)
        return commands(params) if commands else False

## TODO: Implement ###


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

    def handle(self, params: HandlerParams):

        key_sequence = params.keys
        cursor = params.cursor
        modifiers = params.modifiers
        mode = params.mode

        if key_sequence == 'y':
            if mode not in ['VISUAL', 'VISUAL_LINE', 'YANK']:
                print('yank line')
                return self.yank_line(cursor)

            self.registers.update('named', '0', cursor.blockNumber())
            return True

        if key_sequence == 'u':
            self.editor.undo()
            return True

        if 'ctrl' in modifiers and key_sequence == 'r':
            self.editor.redo()
            return True

        if key_sequence == 'p':
            self.editor.paste()
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

    def handle(self, params: HandlerParams):
        if not params.visual:
            return False

        command = self.command_map.get(params.keys)
        return command(params) if command else False

    def delete_text(self, params: HandlerParams) -> bool:
        params.cursor.removeSelectedText()
        super().to_normal_mode()
        return True

    def cut_text(self, params: HandlerParams) -> bool:
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

    def handle(self, params: HandlerParams):

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
