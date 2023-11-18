
from typing import List
from unittest import mock
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_modes import Modes
from vimdcc.handlers.normal import MarksHandler
from vimdcc.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> MarksHandler:
    return MarksHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    jump_to: int


@pytest.mark.parametrize('data', [
    MotionTest(['m', '1'], 4),
    MotionTest(['m', 'a'], 2),
    MotionTest(['m', 'm'], 7),
])
def test_set_mark(handler: MarksHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText('foo\nbar\nfoo\nbar')

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.NORMAL
    )

    params.cursor.setPosition(data.jump_to)

    for motion in data.motion:
        params.keys += motion
        handler.handle(params)

    editor.setTextCursor(params.cursor)

    assert handler.registers.get_mark(data.motion[-1])['position'] == data.jump_to

    params.cursor.setPosition(0)
    editor.setTextCursor(params.cursor)

    assert editor.textCursor().position() == 0

    params.keys = '`'

    # FIXME: Too hacky don't like it...
    preview_marks = mock.Mock()
    preview_marks.get_text_value = lambda: data.jump_to
    handler._preview_marks = preview_marks

    handler.handle(params)
    editor.setTextCursor(params.cursor)

    assert editor.textCursor().position() == data.jump_to
