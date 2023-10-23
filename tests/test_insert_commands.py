from typing import List, cast
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor._types import Modes, EventParams
from nuke_vim_editor.handlers.normal import InsertHandler


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> InsertHandler:
    return InsertHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    expected_text: str
    expected_pos: int


@pytest.mark.parametrize('data', [
    MotionTest(['i'], 'abc', 1, 'a', 0),
    MotionTest(['I'], 'abc', 3, 'a', 0),
    MotionTest(['I'], 'abc', 0, 'a', 0),
    MotionTest(['a'], 'abc', 1, 'c', 2),
    MotionTest(['A'], 'foo bar foo bar', 0, '', 15),
    MotionTest(['o'], 'abc', 0, '', 4),
    MotionTest(['O'], 'abc', 3, '\n', 0),
])
def test_move_document_no_selection(handler: InsertHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)

    params = EventParams(
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

    if data.expected_text:
        assert editor.toPlainText()[position] == data.expected_text

    assert cursor.position() == data.expected_pos
    assert cursor.anchor() == data.expected_pos
    assert cursor.hasSelection() is False
    assert not cursor.selectedText()
