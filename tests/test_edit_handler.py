from typing import List
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.editor_modes import Modes
from nuke_vim_editor.handlers.normal import EditHandler
from nuke_vim_editor.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> EditHandler:
    return EditHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    expected_text: str
    expected_mode: Modes


@pytest.mark.parametrize('data', [
    MotionTest(['x'], 'abc', 1, 'ac', Modes.NORMAL),
    MotionTest(['X'], 'abc', 1, 'bc', Modes.NORMAL),
    MotionTest(['s'], 'abc', 1, 'ac', Modes.INSERT),
    MotionTest(['S'], 'abc', 1, '', Modes.INSERT),
    MotionTest(['cc'], 'abc', 1, '', Modes.INSERT),
    MotionTest(['C'], 'foo bar foo', 4, 'foo ', Modes.INSERT),
    MotionTest(['D'], 'foo bar foo', 4, 'foo ', Modes.NORMAL),
    MotionTest(['dd'], 'foo bar foo', 4, '', Modes.NORMAL),
    MotionTest(['ra'], 'foo bar', 1, 'fao bar', Modes.NORMAL),
])
def test_edit_handler(handler: EditHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)
    handler.mode = Modes.NORMAL

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

    assert editor.toPlainText() == data.expected_text
    assert handler.mode == data.expected_mode
