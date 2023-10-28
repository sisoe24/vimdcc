
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


# @dataclass
# class MotionTest:
#     motion: List[str]
#     text: str
#     cursor_start: int
#     expected_text: str
#     expected_pos: int


def test_set_mark(handler: MarksHandler) -> None:
    editor = handler.editor
    editor.setPlainText('foo\nbar\nfoo\nbar')

    params = EventParams(
        cursor=editor.textCursor(),
        keys='m',
        modifiers=[],
        event=None,
        mode=Modes.NORMAL
    )

    params.cursor.setPosition(7)
    params.keys += 'm1'

    handler.handle(params)
    editor.setTextCursor(params.cursor)

    params.cursor.setPosition(0)

    cursor = editor.textCursor()
    position = cursor.position()

    assert position == 7
