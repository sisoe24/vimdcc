from typing import List
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot

from vimdcc.editor_mode import Modes
from vimdcc.handlers.normal import YankHandler
from vimdcc.handler_parameters import HandlerParams

from vimdcc._qt import QTextCursor, QPlainTextEdit


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> YankHandler:
    return YankHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    expected_text: str
    cursor_start: int


@pytest.mark.parametrize('data', [
    MotionTest(['yy'], 'foo bar', '<LINE_COPY>foo bar\n', 0),
    MotionTest(['Y'], 'foo bar', '<LINE_COPY>foo bar\n', 0),
])
def test_yank_handler(handler: YankHandler, data: MotionTest):
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

    register = handler.registers.get_clipboard()
    assert register[0] == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['yy', 'p'], 'foo bar', 'foo bar\nfoo bar', 0),
    MotionTest(['Y', 'p'], 'foo bar', 'foo bar\nfoo bar', 0),
    MotionTest(['yy', 'P'], 'foo bar', 'foo bar\nfoo bar', 0),
    # P pastes above, p pastes below
    MotionTest(['yy', 'j', 'P'], 'one\ntwo', 'one\none\ntwo', 0),
    MotionTest(['j', 'yy', 'k', 'p'], 'one\ntwo', 'one\ntwo\ntwo', 0),
    # p on the last line goes below it
    MotionTest(['yy', 'j', 'p'], 'one\ntwo', 'one\ntwo\none', 0),
])
def test_paste_handler(handler: YankHandler, data: MotionTest):
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
    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        if motion in ('j', 'k'):
            params.cursor.movePosition(QTextCursor.Down if motion == 'j' else QTextCursor.Up)
            continue
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text
