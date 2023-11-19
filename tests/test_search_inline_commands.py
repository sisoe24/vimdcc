
from typing import List
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_mode import Modes
from vimdcc.handlers.normal import SearchHandler, SearchLineHandler
from vimdcc.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot):
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> SearchLineHandler:
    return SearchLineHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    cursor_end: int


@pytest.mark.parametrize('data', [
    MotionTest(['fb'], 'foo bar', 0, 4),
    MotionTest(['tb'], 'foo bar', 0, 3),
    MotionTest(['Ff'], 'foo bar', 4, 0),
    MotionTest(['Tf'], 'foo bar', 4, 1),
    MotionTest(['fo', ';'], 'foo bar foo', 0, 2),
    MotionTest(['fo', ';', ';'], 'foo bar foo', 0, 9),
    MotionTest(['fo', ';', ';', ','], 'foo bar foo', 0, 2),
    MotionTest(['fo'], 'ambivalent', 0, 0),
    MotionTest(['to'], 'ambivalent', 0, 0),
    MotionTest(['Fo'], 'ambivalent', 9, 9),
    MotionTest(['To'], 'ambivalent', 9, 9),
])
def test_search_inline_hanlder(handler: SearchHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    assert editor.toPlainText() == data.text

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

    assert position == data.cursor_end
