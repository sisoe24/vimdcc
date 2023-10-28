from typing import List, cast
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.editor_modes import Modes
from nuke_vim_editor.handlers.normal import DocumentHandler
from nuke_vim_editor.event_parameters import EventParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> DocumentHandler:
    return DocumentHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    expected_text: str
    expected_pos: int


@pytest.mark.parametrize('data', [
    MotionTest(['gg'], 'foo\nbar\nfoo\nbar', 7, 'f', 0),
    MotionTest(['G'], 'foo\nbar\nfoo\nbar', 0, 'r', 14),
    MotionTest(['{'], 'foo\n\nbar\n\nfoo\n\nbar', 7, '\n', 4),
    MotionTest(['}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, '\n', 4),
    MotionTest(['}', '}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, '\n', 9),
    MotionTest(['}', '}', '}', '}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, 'r', 17),
    MotionTest(['{', '{'], 'foo\n\nbar\n\nfoo\n\nbar', 9, 'f', 0),
])
def test_move_document_no_selection(handler: DocumentHandler, data: MotionTest) -> None:
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

    assert editor.toPlainText()[position] == data.expected_text
    assert cursor.position() == data.expected_pos
    assert cursor.anchor() == data.expected_pos
    assert cursor.hasSelection() is False
    assert not cursor.selectedText()
