
import json
from typing import Dict, List
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor._types import Modes, EventParams
from nuke_vim_editor.handlers.normal import MarksHandler


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> MarksHandler:
    return MarksHandler(editor)


def marks() -> Dict[str, int]:
    with open('marks.json', 'r') as f:
        return json.load(f)


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

    params = EventParams(
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

    assert handler.registers.get('marks', data.motion[-1]) == data.jump_to

    params.cursor.setPosition(0)
    editor.setTextCursor(params.cursor)

    assert editor.textCursor().position() == 0

    params.keys = f'`{data.motion[-1]}'

    handler.handle(params)
    editor.setTextCursor(params.cursor)

    assert editor.textCursor().position() == data.jump_to
