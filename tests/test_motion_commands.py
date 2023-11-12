from typing import List, cast
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.editor_modes import Modes
from nuke_vim_editor.handlers.normal import MotionHandler
from nuke_vim_editor.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> MotionHandler:
    return MotionHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    expected_text: str
    expected_pos: int


@pytest.mark.parametrize('data', [
    MotionTest(['w'], 'foo bar foo bar', 0, 'b', 4),
    MotionTest(['w', 'w'], 'another test\n1', 0, '1', 13),
    MotionTest(['w'], 'another test', 0, 't', 8),
    MotionTest(['w'], 'test\nfoo', 0, 'f', 5),
    MotionTest(['w'], 'test(args)\nfoo', 0, '(', 4),
    MotionTest(['w', 'w'], 'test(args)\nfoo', 0, 'a', 5),
    MotionTest(['b'], 'foo bar foo bar', 4, 'f', 0),
    MotionTest(['b', 'b'], 'another test\n1', 13, 'a', 0),
    MotionTest(['b'], 'another test', 8, 'a', 0),
    MotionTest(['b'], 'test\nfoo', 5, 't', 0),
    MotionTest(['b'], 'test(args)\nfoo', 4, 't', 0),
    MotionTest(['e'], 'foo bar foo bar', 0, 'o', 2),
    MotionTest(['e', 'e'], 'foo bar foo bar', 0, 'r', 6),
    MotionTest(['e', 'e', 'e'], 'foo bar foo bar', 0, 'o', 10),
    MotionTest(['$'], 'foo bar foo bar', 0, 'r', 14),
    MotionTest(['0'], 'foo bar foo bar', 14, 'f', 0),
    MotionTest(['^'], 'foo bar foo bar', 14, 'f', 0),
    MotionTest(['^'], '    foo', 6, 'f', 4),
    MotionTest(['l'], 'foo', 0, 'o', 1),
    MotionTest(['h'], 'foo', 1, 'f', 0),
    MotionTest(['h'], 'foo', 2, 'o', 1),
    MotionTest(['k'], 'foo\nbar', 4, 'f', 0),
    MotionTest(['j'], 'foo\nbar', 0, 'b', 4),
])
def test_motion_no_select(
    handler: MotionHandler,
    data: MotionTest
):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.NORMAL
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()
    position = cursor.position()

    assert editor.toPlainText()[position] == data.expected_text
    assert cursor.position() == data.expected_pos
    assert cursor.anchor() == data.expected_pos
    assert cursor.hasSelection() is False
    assert not cursor.selectedText()


@pytest.mark.parametrize('data', [
    MotionTest(['w'], 'foo bar foo bar', 0, 'foo ', 4),
    MotionTest(['w', 'w'], 'foo bar foo bar', 0, 'foo bar ', 8),
    MotionTest(['w'], 'test\nfoo', 0, 'test\u2029', 5),
    MotionTest(['w'], 'test(args)\nfoo', 0, 'test', 4),
    MotionTest(['b'], 'foo bar foo bar', 14, 'ba', 12),
    MotionTest(['b'], 'foo bar foo bar', 15, 'bar', 12),
    MotionTest(['b', 'b'], 'foo bar foo bar', 15, 'foo bar', 8),
    MotionTest(['e'], 'foo bar foo bar', 0, 'foo', 3),
    MotionTest(['e', 'e'], 'foo bar foo bar', 0, 'foo bar', 7),
    MotionTest(['e', 'e', 'e'], 'foo bar foo bar', 0, 'foo bar foo', 11),
    MotionTest(['$'], 'foo bar foo bar', 0, 'foo bar foo bar', 15),
    MotionTest(['0'], 'foo bar foo bar', 15, 'foo bar foo bar', 0),
    MotionTest(['^'], 'foo bar foo bar', 15, 'foo bar foo bar', 0),
    MotionTest(['^'], '    foo', 7, 'foo', 4),
    MotionTest(['l'], 'foo', 0, 'f', 1),
    MotionTest(['l', 'l'], 'foo', 0, 'fo', 2),
    MotionTest(['h'], 'foo', 1, 'f', 0),
    MotionTest(['h', 'h'], 'foo', 3, 'oo', 1),
    MotionTest(['k'], 'foo\nbar', 4, 'foo\u2029', 0),
    MotionTest(['j'], 'foo\nbar', 0, 'foo\u2029', 4),
    MotionTest(['j'], 'foo\nbar', 2, 'o\u2029ba', 6),
])
def test_motion_select(handler: MotionHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()
    assert cursor.position() == data.expected_pos
    assert cursor.anchor() == data.cursor_start
    assert cursor.hasSelection() is True
    assert cursor.selectedText() == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['y', 'w'], 'foo bar', 0, 'foo ', 0),
    MotionTest(['y', 'e'], 'foo bar', 0, 'foo', 0),
    MotionTest(['y', 'b'], 'foo bar', 7, 'bar', 7),
    MotionTest(['y', '$'], 'foo bar', 0, 'foo bar', 0),
    MotionTest(['y', '0'], '  foo bar', 9, '  foo bar', 9),
    MotionTest(['y', '^'], '  foo bar', 9, 'foo bar', 9),
    MotionTest(['y', 'l'], 'foo bar', 0, 'f', 0),
    MotionTest(['y', 'h'], 'foo bar', 1, 'f', 1),
    MotionTest(['y', 'j'], 'foo\nbar', 0, 'foo\u2029bar', 0),
    MotionTest(['y', 'j'], 'foo\nbar', 3, 'foo\u2029bar', 3),
    MotionTest(['y', 'k'], 'foo\nbar', 4, 'foo\u2029bar', 4),
    MotionTest(['y', 'k'], 'foo\nbar', 7, 'foo\u2029bar', 7),
])
def test_motion_yank(handler: MotionHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.YANK
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()

    assert cursor.position() == data.expected_pos

    register = handler.registers.get_register('numbered')
    assert register[0] == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['c', 'w'], 'foo bar', 0, 'bar', 0),
    MotionTest(['c', 'e'], 'foo bar', 0, ' bar', 0),
    MotionTest(['c', 'b'], 'foo bar', 7, 'foo ', 4),
    MotionTest(['c', '$'], 'foo bar', 0, '', 0),
    MotionTest(['c', '0'], '  foo bar', 9, '', 0),
    MotionTest(['c', '^'], '  foo bar', 9, '  ', 2),
    MotionTest(['c', 'l'], 'foo bar', 0, 'oo bar', 0),
    MotionTest(['c', 'h'], 'foo bar', 1, 'oo bar', 0),
    MotionTest(['c', 'j'], 'foo\nbar', 0, '', 0),
    MotionTest(['c', 'j'], 'foo\nbar', 3, '', 0),
    MotionTest(['c', 'k'], 'foo\nbar', 4, '', 0),
    MotionTest(['c', 'k'], 'foo\nbar', 7, '', 0),
])
def test_motion_edit_change(handler: MotionHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.CHANGE
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()

    assert cursor.position() == data.expected_pos
    assert editor.toPlainText() == data.expected_text

    # TODO: Should test if the mode is changed to INSERT but it doesn't work
    # if I call the handler since its not it who changes the mode
    # assert handler.mode == Modes.INSERT


@pytest.mark.parametrize('data', [
    MotionTest(['d', 'w'], 'foo bar', 0, 'bar', 0),
    MotionTest(['d', 'e'], 'foo bar', 0, ' bar', 0),
    MotionTest(['d', 'b'], 'foo bar', 7, 'foo ', 4),
    MotionTest(['d', '$'], 'foo bar', 0, '', 0),
    MotionTest(['d', '0'], '  foo bar', 9, '', 0),
    MotionTest(['d', '^'], '  foo bar', 9, '  ', 2),
    MotionTest(['d', 'l'], 'foo bar', 0, 'oo bar', 0),
    MotionTest(['d', 'h'], 'foo bar', 1, 'oo bar', 0),
    MotionTest(['d', 'j'], 'foo\nbar', 0, '', 0),
    MotionTest(['d', 'j'], 'foo\nbar', 3, '', 0),
    MotionTest(['d', 'k'], 'foo\nbar', 4, '', 0),
    MotionTest(['d', 'k'], 'foo\nbar', 7, '', 0),
])
def test_motion_edit_delete(handler: MotionHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.CHANGE
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()

    assert cursor.position() == data.expected_pos
    assert editor.toPlainText() == data.expected_text
