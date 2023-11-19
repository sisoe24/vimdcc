
from typing import List
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_mode import Modes
from vimdcc.handlers.normal import TextObjectsHandler
from vimdcc.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def handler(editor: QPlainTextEdit) -> TextObjectsHandler:
    return TextObjectsHandler(editor)


@dataclass
class MotionTest:
    motion: List[str]
    text: str
    cursor_start: int
    expected_text: str
    expected_mode: Modes


@pytest.mark.parametrize('data', [
    MotionTest(['ci('], 'foo(bar)', 3, 'foo()', Modes.INSERT),
    MotionTest(['ca('], 'foo(bar)', 3, 'foo', Modes.INSERT),
    MotionTest(['ci['], 'foo[bar]', 3, 'foo[]', Modes.INSERT),
    MotionTest(['ca['], 'foo[bar]', 3, 'foo', Modes.INSERT),
    MotionTest(['ci{'], 'foo{bar}', 3, 'foo{}', Modes.INSERT),
    MotionTest(['ca{'], 'foo{bar}', 3, 'foo', Modes.INSERT),
    MotionTest(['ci"'], 'foo"bar"', 3, 'foo""', Modes.INSERT),
    MotionTest(['ca"'], 'foo"bar"', 3, 'foo', Modes.INSERT),
    MotionTest(['ci\''], 'foo\'bar\'', 3, 'foo\'\'', Modes.INSERT),
    MotionTest(['ca\''], 'foo\'bar\'', 3, 'foo', Modes.INSERT),
    MotionTest(['ci`'], 'foo`bar`', 3, 'foo``', Modes.INSERT),
    MotionTest(['ci('], 'foo(bar, \n, bar, \n, bar)', 3, 'foo()', Modes.INSERT)
])
def test_text_object_handler(handler: TextObjectsHandler, data: MotionTest) -> None:
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

    params.keys = data.motion[0]
    handler.handle(params)
    editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()
    text = editor.toPlainText()

    assert text == data.expected_text
