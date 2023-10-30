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


@pytest.fixture(scope='function')
def params(editor: QPlainTextEdit) -> HandlerParams:
    return HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.NORMAL
    )


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
        keys=data.motion,
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
def test_motion_select(
    handler: MotionHandler,
    data: MotionTest
):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys=data.motion,
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
