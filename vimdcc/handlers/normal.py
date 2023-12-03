from __future__ import annotations

from typing import Dict, Callable, Optional

from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..editor_mode import Modes, EditorMode
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

    def _get_word_under_cursor(self, cursor: QTextCursor) -> str:
        initial_position = cursor.position()
        cursor.select(QTextCursor.WordUnderCursor)
        text = cursor.selectedText()
        cursor.setPosition(initial_position)
        return text

    def _move_cursor(self, params: HandlerParams, move_func: Callable[[int], Optional[int]]):
        cursor = params.cursor
        start = cursor.position()
        pos = move_func(cursor.position())
        if pos is not None:

            # TODO: Refactor: Many similarity with the _set_cursor method from SearchLineHandler
            select = QTextCursor.MoveAnchor
            if EditorMode.mode in [Modes.CHANGE, Modes.DELETE, Modes.YANK, Modes.VISUAL]:
                cursor.setPosition(start, QTextCursor.MoveAnchor)
                select = QTextCursor.KeepAnchor

            cursor.setPosition(pos, select)

            if EditorMode.mode in [Modes.CHANGE, Modes.DELETE]:
                cursor.removeSelectedText()

            elif EditorMode.mode == Modes.YANK:
                self.registers.add(cursor.selectedText())
                cursor.clearSelection()
                cursor.setPosition(start, QTextCursor.MoveAnchor)

        return True

    def go_up(self, params: HandlerParams):
        return self._move_cursor(params, self.search.find_next_up)

    def go_down(self, params: HandlerParams):
        return self._move_cursor(params, self.search.find_next_down)

    def search_down(self, params: HandlerParams, key: str):
        self.registers.add_last_search(key)
        self.search.find(key)
        return self.go_down(params)

    def search_up(self, params: HandlerParams, key: str):
        self.registers.add_last_search(key)
        self.search.find(key)
        return self.go_up(params)

    def search_down_under_cursor(self, params: HandlerParams):
        return self.search_down(params, self._get_word_under_cursor(params.cursor))

    def search_up_under_cursor(self, params: HandlerParams):
        return self.search_up(params, self._get_word_under_cursor(params.cursor))

    def search_word_up(self, params: HandlerParams, key: str):
        return self.search_up(params, key)

    def search_word_down(self, params: HandlerParams, key: str):
        return self.search_down(params, key)

    def handle(self, params: HandlerParams) -> bool:
        key = params.event.key()
        key_sequence = params.keys

        if key_sequence.startswith('?') and key == 16777220:
            return self.search_word_up(params, key_sequence[1:])

        if key_sequence.startswith('/') and key == 16777220:
            return self.search_word_down(params, key_sequence[1:])

        command = self.commands.get(params.keys)
        return command(params) if command else False


@register_normal_handler
class SearchLineHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.search = SearchCommand(editor)
        self.commands = {
            ';': self.search_forward_again,
            ',': self.search_backward_again,
        }
        # TODO: This is a mess. Refactor this.
        # TODO: Add tests for c, d, y, v

    def _set_cursor(
        self,
        start: int,
        cursor: QTextCursor,
        pos: Optional[int],
        move_char: QTextCursor.MoveOperation = QTextCursor.NoMove
    ):
        if pos is None:
            return False

        # anchor the cursor if we are in any of the modes
        select = QTextCursor.MoveAnchor
        if EditorMode.mode in [Modes.CHANGE, Modes.DELETE, Modes.YANK, Modes.VISUAL]:
            cursor.setPosition(start, QTextCursor.MoveAnchor)
            select = QTextCursor.KeepAnchor

        # set the cursor to destination
        cursor.setPosition(pos, select)

        if EditorMode.mode in [Modes.CHANGE, Modes.DELETE]:
            cursor.movePosition(move_char, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        elif EditorMode.mode == Modes.YANK:
            cursor.movePosition(move_char, QTextCursor.KeepAnchor)
            self.registers.add(cursor.selectedText())
            cursor.clearSelection()
            cursor.setPosition(start, QTextCursor.MoveAnchor)

        elif EditorMode.mode == Modes.VISUAL:
            cursor.movePosition(move_char, QTextCursor.KeepAnchor)

        return True

    def search_forward(
        self,
        params: HandlerParams,
        key: str,
        move_char: QTextCursor.MoveOperation = QTextCursor.NextCharacter
    ):
        """f + key."""
        self.search.find(key)
        cursor = params.cursor
        start = cursor.position()
        pos = self.search.find_next_down(start)
        return self._set_cursor(start, cursor, pos, move_char)

    def search_backward(
        self,
        params: HandlerParams,
        key: str,
        move_char: QTextCursor.MoveOperation = QTextCursor.NoMove
    ):
        """F + key."""
        self.search.find(key)
        cursor = params.cursor
        start = cursor.position()
        pos = self.search.find_next_up(cursor.position())
        return self._set_cursor(start, cursor, pos, move_char)

    def search_forward_before(self, params: HandlerParams, key: str):
        """t + key."""
        if not self.search_forward(params, key, QTextCursor.NextCharacter):
            return False
        params.cursor.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
        return True

    def search_backward_before(self, params: HandlerParams, key: str):
        """T + key."""
        if not self.search_backward(params, key, QTextCursor.NextCharacter):
            return False
        params.cursor.movePosition(QTextCursor.NextCharacter)
        return True

    def search_forward_again(self, params: HandlerParams):
        start = params.cursor.position()
        pos = self.search.find_next_down(start)
        return self._set_cursor(start, params.cursor, pos)

    def search_backward_again(self, params: HandlerParams):
        start = params.cursor.position()
        pos = self.search.find_next_up(start)
        return self._set_cursor(start, params.cursor, pos)

    def handle(self, params: HandlerParams):
        keys = params.keys

        if keys.startswith('f') and len(keys) == 2:
            self.search_forward(params, keys[1])
            return True

        if keys.startswith('F') and len(keys) == 2:
            self.search_backward(params, keys[1])
            return True

        if keys.startswith('t') and len(keys) == 2:
            self.search_forward_before(params, keys[1])
            return True

        if keys.startswith('T') and len(keys) == 2:
            self.search_backward_before(params, keys[1])
            return True

        commands = self.commands.get(keys)
        return commands(params) if commands else False


@register_normal_handler
class YankHandler(BaseHandler):
    # token to identify that the copied text contains a new line
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

    def _paste(self, params: HandlerParams, text: Optional[str] = None):
        if not text:
            return True

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
        if params.keys == "'":
            return self.preview_register(params)

        if params.keys == '\\':
            return self.preview_clipboard(params)

        commands = self.commands.get(params.keys)
        return commands(params) if commands else False

    def preview_clipboard(self, params: HandlerParams):
        previewer = self._numbered_register
        value = previewer.get_text_value()
        if value:
            self._paste(params, value)
        return True

    def preview_register(self, params: HandlerParams):
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

        self.word = {
            'w': self.delete_word,
        }

        self.valid_operators = {'ci', 'ca', 'di', 'da', 'vi', 'va', 'yi', 'ya'}
        self.text_obj_mode = ''

    def _execute_text_object(self, cursor: QTextCursor, operator: str, start: int, end: int):
        # TODO: Refactor this method

        if operator[1] == 'i':
            start += 1
        elif operator[1] == 'a':
            end += 1

        cursor.setPosition(start, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)

        # when in visual or yank mode, we dont need to delete the text
        # so we stop before

        if self.text_obj_mode == 'VISUAL':
            return True

        self.registers.add(cursor.selectedText())

        if self.text_obj_mode == 'YANK':
            cursor.clearSelection()
            return True

        cursor.removeSelectedText()

        if operator[0] == 'c':
            super().to_insert_mode()

        return True

    def find_text_object_quote(
        self, cursor: QTextCursor, quote_type: MatchingCharacter, operator: str
    ):

        line_end_position = cursor.block().position() + cursor.block().length() - 1
        find = find_matching(self.editor.toPlainText(), quote_type,
                             cursor.position(), line_end_position)
        if find:
            self._execute_text_object(cursor, operator, find[0], find[1])
        return True

    def find_text_object_bracket(
        self, cursor: QTextCursor, bracket_type: MatchingCharacter, operator: str
    ):
        find = find_matching(self.editor.toPlainText(), bracket_type, cursor.position())
        if find:
            self._execute_text_object(cursor, operator, find[0], find[1])
        return True

    def delete_word(self, cursor: QTextCursor, operator: str):
        # TODO: i and a are the same: It does not handle the around spaces
        if operator[1] == 'a':
            operator = 'di'

        if self.editor.toPlainText()[cursor.position() - 1] != ' ':
            cursor.movePosition(QTextCursor.PreviousWord, QTextCursor.MoveAnchor)

        start_pos = cursor.position() - 1

        cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
        end_pos = cursor.position()
        return self._execute_text_object(cursor, operator, start_pos, end_pos)

    def handle(self, params: HandlerParams) -> bool:

        self.text_obj_mode = ''

        keys = params.keys
        if not keys or len(keys) < 3:
            return False

        operator = keys[:2]  # di, ci, da, ca, yi, ya, vi, va
        character = keys[-1]  # (, ), {, }, [, ], ', ", `

        if operator not in self.valid_operators:
            return False

        if operator[0] == 'v':
            self.text_obj_mode = 'VISUAL'
            # HACK: change the mode to visual so that the VisualEditHandler can handle it
            super().to_visual_mode()
        elif operator[0] == 'y':
            self.text_obj_mode = 'YANK'

        if character in self.brackets:
            bracket_type = self.brackets[character]
            return self.find_text_object_bracket(params.cursor, bracket_type, operator)

        if character in self.quotes:
            quote_type = self.quotes[character]
            return self.find_text_object_quote(params.cursor, quote_type, operator)

        if character in self.word:
            return self.delete_word(params.cursor, operator)

        return False


@register_normal_handler
class TextSearchObjectsHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: HandlerParams) -> bool:

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
        if cursor.block().text().strip() == '':
            cursor.deleteChar()
        else:
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            super().add_to_clipboard(cursor.selectedText() + '\n')
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


@register_normal_handler
class UndoRedoHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.commands = {
            'u': self.undo,
            '®': self.redo
        }

    def undo(self, params: HandlerParams):
        self.editor.undo()
        return True

    def redo(self, params: HandlerParams):
        # TODO: Currently redo is under the ® key, but it should be under the
        # <C-r> key.
        self.editor.redo()
        return True

    def handle(self, params: HandlerParams):
        commands = self.commands.get(params.keys)
        return commands(params) if commands else False
