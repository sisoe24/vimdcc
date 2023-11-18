from __future__ import annotations

from typing import Dict, Optional

from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import BaseCommand, MoveCommand
from ..handler_base import BaseHandler, register_normal_handler
from ..text_objects import MatchingCharacter, find_matching
from ..commands.insert import (Inserta, InsertA, Inserti, InsertI, InsertO,
                               Inserto)
from ..commands.search import SearchCommand
from ..commands.motions import (MoveLineUp, MoveLineEnd, MoveLineDown,
                                MoveWordLeft, MoveLineStart, MoveWordRight,
                                MoveWordForward, MoveWordBackward,
                                MoveToStartOfBlock, MoveWordForwardEnd)
from ..commands.document import (MoveDocumentUp, MoveParagraphUp,
                                 MoveDocumentDown, MoveParagraphDown)
from ..registers_preview import (PreviewMarkRegister, PreviewNamedRegister,
                                 PreviewNumberedRegister)
from ..commands.swap_case import SwapCase, SwapLower, SwapUpper
from ..handler_parameters import HandlerParams


@register_normal_handler
class MotionHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, MoveCommand] = {
            'w': MoveWordForward(editor),
            'b': MoveWordBackward(editor),
            'e': MoveWordForwardEnd(editor),
            'h': MoveWordLeft(editor),
            'l': MoveWordRight(editor),
            'k': MoveLineUp(editor),
            'j': MoveLineDown(editor),
            '$': MoveLineEnd(editor),
            '0': MoveLineStart(editor),
            '^': MoveToStartOfBlock(editor),
        }

    def handle(self, params: HandlerParams):
        command = self.commands.get(params.keys)
        return command.execute(params) if command else False


@register_normal_handler
class DocumentHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, MoveCommand] = {
            'G': MoveDocumentDown(editor),
            'gg': MoveDocumentUp(editor),
            '{': MoveParagraphUp(editor),
            '}': MoveParagraphDown(editor),
        }

    def handle(self, params: HandlerParams):
        command = self.commands.get(params.keys)
        return command.execute(params) if command else False


@register_normal_handler
class InsertHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, BaseCommand] = {
            'i': Inserti(editor),
            'I': InsertI(editor),
            'a': Inserta(editor),
            'A': InsertA(editor),
            'o': Inserto(editor),
            'O': InsertO(editor),
        }

    def handle(self, params: HandlerParams):
        if params.mode != 'NORMAL':
            return False

        command = self.commands.get(params.keys)
        if command and command.execute(params):
            super().to_insert_mode()
            return True
        return False


@register_normal_handler
class SwapCaseHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands: Dict[str, BaseCommand] = {
            '~': SwapCase(editor),
            'g~': SwapCase(editor),
            'gu': SwapLower(editor),
            'gU': SwapUpper(editor),
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
        self._preview_marks = PreviewMarkRegister()

    def set_mark(self, key: str, params: HandlerParams):
        current_line_text = params.cursor.block().text().strip()
        self.registers.add_mark(key, current_line_text, params.cursor.position())
        return True

    def go_to_mark(self, params: HandlerParams):
        previewer = self._preview_marks
        value = previewer.get_text_value()
        if value is not None:
            params.cursor.setPosition(int(value))
        return True

    def handle(self, params: HandlerParams):
        key_sequence = params.keys

        if key_sequence.startswith('m') and len(key_sequence) == 2:
            return self.set_mark(key_sequence[1], params)

        return self.go_to_mark(params) if key_sequence == '`' else False


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
        self.registers.add_last_search(key)
        self.search.find(key)
        return self.go_down(params)

    def _search_up(self, params: HandlerParams, key: str):
        self.registers.add_last_search(key)
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


@register_normal_handler
class YankHandler(BaseHandler):
    LINE_COPY = '<LINE_COPY>'

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands = {
            'yy': self.yank_line,
            'Y': self.yank_line,
            'p': self.paste,
            'P': self.paste_before,
        }
        self._named_register = PreviewNamedRegister()
        self._numbered_register = PreviewNumberedRegister()

    def _paste(self, params: HandlerParams, text: str):
        cursor = params.cursor
        if self.LINE_COPY in text:
            text = text.replace(self.LINE_COPY, '')
            cursor.movePosition(QTextCursor.Down)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(text)
            cursor.movePosition(QTextCursor.Up)
        else:
            cursor.insertText(text)
            cursor.movePosition(QTextCursor.PreviousCharacter)

    def paste(self, params: HandlerParams):
        params.cursor.movePosition(QTextCursor.NextCharacter)
        self.editor.setTextCursor(params.cursor)
        self._paste(params, self.registers.get_named_register_value())
        return True

    def paste_before(self, params: HandlerParams):
        self._paste(params, self.registers.get_named_register_value())
        return True

    def yank_line(self, params: HandlerParams):
        cursor = params.cursor
        pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.registers.add(self.LINE_COPY + cursor.selectedText() + '\n')
        cursor.clearSelection()
        cursor.setPosition(pos)
        return True

    def handle(self, params: HandlerParams):
        if params.keys == '"':
            return self.preview_register()

        if params.keys == "'":
            return self.preview_clipboard()

        commands = self.commands.get(params.keys)
        return commands(params) if commands else False

    def preview_clipboard(self):
        previewer = self._numbered_register
        value = previewer.get_text_value()
        if value:
            self._paste(value)
        return True

    def preview_register(self):
        previewer = self._named_register
        value = previewer.get_text_value()
        if value:
            self.registers.set_named_register(value)
        return True


@register_normal_handler
class VisualEditHandler(BaseHandler):
    """Visual mode edit handler.

    Although it's called visual edit handler, it handles the commands from the
    NORMAL mode. I dont have enough reasons to create a new mode for this.
    """

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.command_map = {
            'c': self.cut_text,
            'd': self.delete_text,
            'y': self.yank_text,
        }

    def handle(self, params: HandlerParams):
        if params.mode not in ['VISUAL', 'VISUAL_LINE']:
            return False

        command = self.command_map.get(params.keys)
        return command(params) if command else False

    def yank_text(self, params: HandlerParams) -> bool:
        super().add_to_clipboard(params.cursor.selectedText())
        params.cursor.clearSelection()
        super().to_normal_mode()
        return True

    def delete_text(self, params: HandlerParams) -> bool:
        super().add_to_clipboard(params.cursor.selectedText())
        params.cursor.removeSelectedText()
        super().to_normal_mode()
        return True

    def cut_text(self, params: HandlerParams) -> bool:
        super().add_to_clipboard(params.cursor.selectedText())
        params.cursor.removeSelectedText()
        super().to_insert_mode()
        return True


@register_normal_handler
class TextObjectsHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.brackets = {
            '(': MatchingCharacter.PARENTHESIS,
            ')': MatchingCharacter.PARENTHESIS,
            '{': MatchingCharacter.BRACKETS,
            '}': MatchingCharacter.BRACKETS,
            '[': MatchingCharacter.SQUARE_BRACKETS,
            ']': MatchingCharacter.SQUARE_BRACKETS,
        }

        self.quotes = {
            "'": MatchingCharacter.SINGLE_QUOTES,
            '`': MatchingCharacter.BACKTICK,
            '"': MatchingCharacter.DOUBLE_QUOTES,
        }

        self.valid_operators = {'ci', 'ca', 'di', 'da'}

    def _execute_text_object(self, cursor: QTextCursor, operator: str, start: int, end: int):
        if operator[1] == 'i':
            start += 1
        elif operator[1] == 'a':
            end += 1

        cursor.setPosition(start, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.registers.add(cursor.selectedText())
        cursor.removeSelectedText()

        if operator[0] == 'c':
            super().to_insert_mode()

        return True

    def execute_text_object_quote(
        self, cursor: QTextCursor, quote_type: MatchingCharacter, operator: str
    ):

        line_end_position = cursor.block().position() + cursor.block().length() - 1
        find = find_matching(self.editor.toPlainText(), quote_type,
                             cursor.position(), line_end_position)
        if find:
            self._execute_text_object(cursor, operator, find[0], find[1])
        return True

    def execute_text_object_bracket(
        self, cursor: QTextCursor, bracket_type: MatchingCharacter, operator: str
    ):
        find = find_matching(self.editor.toPlainText(), bracket_type, cursor.position())
        if find:
            self._execute_text_object(cursor, operator, find[0], find[1])
        return True

    def handle(self, params: HandlerParams) -> bool:
        keys = params.keys
        if not keys or len(keys) < 3:
            return False

        operator = keys[:2]  # di, ci, da, ca
        character = keys[-1]  # (, ), {, }, [, ], ', ", `

        if operator in self.valid_operators and character in self.brackets:
            bracket_type = self.brackets[character]
            return self.execute_text_object_bracket(params.cursor, bracket_type, operator)

        if operator in self.valid_operators and character in self.quotes:
            quote_type = self.quotes[character]
            return self.execute_text_object_quote(params.cursor, quote_type, operator)

        return False


@register_normal_handler
class EditHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands = {
            'x': self._delete_char,
            'X': self._delete_char_before,
            's': self._delete_char_insert,
            'S': self._delete_line_insert,
            'cc': self._delete_line_insert,
            'C': self._delete_from_cursor_insert,
            'D': self._delete_from_cursor,
            'dd': self._delete_line,
        }

    def _delete_from_cursor(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        super().add_to_clipboard(cursor.selectedText())
        cursor.removeSelectedText()
        return True

    def _delete_from_cursor_insert(self, cursor: QTextCursor):
        super().to_insert_mode()
        self._delete_from_cursor(cursor)
        return True

    def _delete_char(self, cursor: QTextCursor):
        cursor.deleteChar()
        return True

    def _delete_char_before(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.PreviousCharacter)
        cursor.deleteChar()
        return True

    def _delete_char_insert(self, cursor: QTextCursor):
        super().to_insert_mode()
        cursor.deleteChar()
        return True

    def _replace_char(self, cursor: QTextCursor, key: str):
        cursor.movePosition(QTextCursor.NextCharacter)
        cursor.deletePreviousChar()
        cursor.insertText(key)
        return True

    def _delete_line(self, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        super().add_to_clipboard(cursor.selectedText())
        cursor.removeSelectedText()
        return True

    def _delete_line_insert(self, cursor: QTextCursor):
        self._delete_line(cursor)
        super().to_insert_mode()
        return True

    def handle(self, params: HandlerParams):
        keys = params.keys

        if keys.startswith('r') and len(keys) == 2:
            return self._replace_char(params.cursor, keys[1])

        commands = self.commands.get(keys)
        return commands(params.cursor) if commands else False
