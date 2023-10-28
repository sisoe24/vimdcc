from typing import List, cast
from dataclasses import dataclass

import pytest
from PySide2.QtGui import QTextCursor
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor._types import Modes, EventParams
from nuke_vim_editor.handlers.normal import SwapCaseHandler


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> SwapCaseHandler:
    return SwapCaseHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    expected_text: str
    cursor_start: int
    cursor_end: int


@pytest.mark.parametrize('data', [
    MotionTest(['g~'], 'aBa', 'AbA', 0, 3),
    MotionTest(['gu'], 'AB', 'ab', 0, 2),
    MotionTest(['gU'], 'ab', 'AB', 0, 2),
])
def test_swap_case_motion(handler: SwapCaseHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = EventParams(
        cursor=editor.textCursor(),
        keys=data.motion,
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.setPosition(data.cursor_start)
    params.cursor.setPosition(data.cursor_end, QTextCursor.KeepAnchor)

    params.keys = data.motion[0]
    handler.handle(params)
    editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text
