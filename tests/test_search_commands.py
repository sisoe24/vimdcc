
from typing import List
from dataclasses import dataclass

import pytest
from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt, QEvent
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.editor_modes import Modes
from nuke_vim_editor.commands.search import (SearchCommand, _find,
                                             _find_next_up, _find_next_down)
from nuke_vim_editor.handlers.normal import SearchHandler
from nuke_vim_editor.handler_parameters import HandlerParams


@pytest.mark.parametrize('string, search, positions', [
    ('This is a string', 'is', [2, 5]),
    ('The out of this output is output', 'out', [4, 16, 26]),
    ('The out of this output is output', 'output', [16, 26]),
    ('The energy of the electron is 1.2e-19', 'e', [2, 4, 6, 16, 18, 20, 33])
])
def test_find_string(string: str, search: str, positions: list[int]):
    assert _find(search, string) == positions


@pytest.mark.parametrize('positions, start_position, next_position', [
    ([2, 5, 10], 2, 10),
    ([2, 5, 10], 3, 2),
    ([2, 5, 10], 5, 2),
    ([2, 5, 10], 1, 10),
    ([2, 5, 10], 7, 5),
    ([2, 5, 10], 10, 5),
    ([2, 5, 10], 0, 10),
    ([0, 5, 10], 0, 10),
    ([2, 5, 10], 11, 10),
])
def test_find_next_up(positions: list[int], start_position: int, next_position: int):
    assert _find_next_up(positions, start_position) == next_position


@pytest.mark.parametrize('positions, start_position, next_position', [
    ([2, 5, 10], 2, 5),
    ([2, 5, 10], 3, 5),
    ([2, 5, 10], 5, 10),
    ([2, 5, 10], 1, 2),
    ([2, 5, 10], 7, 10),
    ([2, 5, 10], 10, 2),
    ([2, 5, 10], 0, 2),
    ([2, 5, 10], 11, 2),
])
def test_find_next_down(positions: list[int], start_position: int, next_position: int):
    assert _find_next_down(positions, start_position) == next_position


@pytest.fixture()
def editor(qtbot: QtBot):
    return QPlainTextEdit()


def test_search_command(editor: QPlainTextEdit):
    editor.setPlainText('This is a string')

    search = SearchCommand(editor)
    search.find('is')

    assert search.history == [2, 5]

    cursor = editor.textCursor()
    assert cursor.position() == 0

    next_down = search.find_next_down(cursor.position())
    assert next_down == 2

    next_down = search.find_next_down(next_down)
    assert next_down == 5

    next_down = search.find_next_down(next_down)
    assert next_down == 2

    next_up = search.find_next_up(next_down)
    assert next_up == 5

    next_up = search.find_next_up(next_up)
    assert next_up == 2


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> SearchHandler:
    return SearchHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    search: str
    text: str
    cursor_start: int
    cursor_end: int


@pytest.mark.parametrize('data', [
    MotionTest(['n'], 'foo', 'foo bar foo bar foo bar foo', 0, 8),
    MotionTest(['n', 'n'], 'foo', 'foo bar foo bar foo bar foo', 0, 16),
    MotionTest(['n', 'n', 'n'], 'foo', 'foo bar foo bar foo bar foo', 0, 24),
    MotionTest(['N'], 'foo', 'foo bar foo bar foo bar foo', 24, 16),
    MotionTest(['N', 'N'], 'foo', 'foo bar foo bar foo bar foo', 24, 8),
    MotionTest(['N', 'N', 'N'], 'foo', 'foo bar foo bar foo bar foo', 24, 0),
])
def test_search_hanlder(handler: SearchHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    handler.search.find(data.search)

    assert editor.toPlainText() == data.text
    assert handler.search.history == [0, 8, 16, 24]

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.NoModifier),
        mode=Modes.NORMAL
    )

    params.cursor.setPosition(data.cursor_start)
    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()
    position = cursor.position()

    assert position == data.cursor_end


@pytest.mark.parametrize('data', [
    MotionTest(['n'], 'import', 'foo bar foo bar foo bar foo', 0, 0),
    MotionTest(['N'], 'import', 'foo bar foo bar foo bar foo', 0, 0),
])
def test_search_hanlder_no_match(handler: SearchHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    handler.search.find(data.search)

    assert editor.toPlainText() == data.text

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys=data.motion[0],
        modifiers=[],
        event=QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.NoModifier),
        mode=Modes.NORMAL
    )

    params.cursor.setPosition(data.cursor_start)
    handler.handle(params)
    editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()
    position = cursor.position()

    assert position == data.cursor_end


@pytest.mark.parametrize('string, pos, word', [
    ('foo bar', 0, 'foo'),
    ('foo bar', 1, 'foo'),
    ('foo bar', 3, 'foo'),
    ('foo      bar', 5, 'foo'),
    ('foo bar', 4, 'bar'),
])
def test_search_hanlder_word_under_cursor(
    handler: SearchHandler,
    string: str,
    pos: int,
    word: str
):
    editor = handler.editor
    editor.setPlainText(string)
    cursor = editor.textCursor()
    cursor.setPosition(pos)
    assert handler.get_word_under_cursor(cursor) == word


def test_search_hanlder_word_under_cursor_up(handler: SearchHandler):
    editor = handler.editor
    editor.setPlainText('foo bar foo bar foo bar foo')

    SearchCommand(handler.editor)

    cursor = editor.textCursor()
    cursor.setPosition(0)

    params = HandlerParams(
        cursor=cursor,
        keys='',
        modifiers=[],
        event=QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.NoModifier),
        mode=Modes.NORMAL
    )

    handler.search_down_under_cursor(params)
    assert params.cursor.position() == 8

    handler.search_down_under_cursor(params)
    assert params.cursor.position() == 16

    handler.search_down_under_cursor(params)
    assert params.cursor.position() == 24

    handler.search_down_under_cursor(params)
    assert params.cursor.position() == 0

    handler.search_down_under_cursor(params)
    assert params.cursor.position() == 8

    handler.search_up_under_cursor(params)
    assert params.cursor.position() == 0

    handler.search_up_under_cursor(params)
    assert params.cursor.position() == 24

    handler.search_up_under_cursor(params)
    assert params.cursor.position() == 16
