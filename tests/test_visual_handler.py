from typing import List
from dataclasses import dataclass

import pytest
from PySide2.QtGui import QTextCursor
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_mode import Modes
from vimdcc.handlers.normal import VisualEditHandler
from vimdcc.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> VisualEditHandler:
    return VisualEditHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    copied_text: str
    editor_text: str


@pytest.mark.parametrize('data', [
    MotionTest(['y'], 'foo bar', 'foo bar', 'foo bar'),
    MotionTest(['d'], 'foo bar', 'foo bar', ''),
    MotionTest(['c'], 'foo bar', 'foo bar', ''),
])
def test_visual_handler(handler: VisualEditHandler, data: MotionTest):
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys=data.motion[0],
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
    params.cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

    handler.handle(params)
    editor.setTextCursor(params.cursor)

    register = handler.registers.get_clipboard()
    assert register[0] == data.copied_text
    assert editor.toPlainText() == data.editor_text
