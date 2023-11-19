from typing import List
from dataclasses import dataclass

import pytest
from PySide2.QtGui import QTextCursor
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_modes import Modes
from vimdcc.handlers.normal import YankHandler
from vimdcc.handler_parameters import HandlerParams


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

    register = handler.registers.get_register('clipboard')
    assert register[0] == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['yy', 'p'], 'foo bar', 'foo bar\nfoo bar', 0),
    MotionTest(['Y', 'p'], 'foo bar', 'foo bar\nfoo bar', 0),
    MotionTest(['yy', 'P'], 'foo bar', 'foo bar\nfoo bar', 0),
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
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text
