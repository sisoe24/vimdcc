from typing import List, cast
from dataclasses import dataclass

import pytest
from PySide2.QtGui import QTextCursor
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from vimdcc.editor_modes import Modes
from vimdcc.handlers.normal import MotionHandler, SwapCaseHandler
from vimdcc.handler_parameters import HandlerParams


@pytest.fixture()
def editor(qtbot: QtBot) -> QPlainTextEdit:
    return QPlainTextEdit()


@pytest.fixture()
def swapCaseHandler(editor: QPlainTextEdit) -> SwapCaseHandler:
    return SwapCaseHandler(editor)


@pytest.fixture()
def motionHandler(editor: QPlainTextEdit) -> MotionHandler:
    return MotionHandler(editor)


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
def test_swap_case_motion(swapCaseHandler: SwapCaseHandler, data: MotionTest):
    editor = swapCaseHandler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys=data.motion,
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.setPosition(data.cursor_start)
    params.cursor.setPosition(data.cursor_end, QTextCursor.KeepAnchor)

    params.keys = data.motion[0]
    swapCaseHandler.handle(params)
    editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text


@dataclass
class MotionSelectionTest:
    motion: str
    command: str
    text: str
    expected_text: str
    cursor_start: int
    cursor_end: int


@pytest.mark.parametrize('data', [
    MotionSelectionTest('e', 'g~', 'aBa', 'AbA', 0, 3),
    MotionSelectionTest('e', 'gu', 'AB', 'ab', 0, 2),
    MotionSelectionTest('e', 'gU', 'ab', 'AB', 0, 2),
])
def test_swap_case_motion_with_motion(
    motionHandler: MotionHandler,
    swapCaseHandler: SwapCaseHandler,
    data: MotionTest
):
    editor = motionHandler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys=data.motion,
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.setPosition(data.cursor_start)
    params.keys = data.motion

    motionHandler.handle(params)

    params.keys = data.command
    swapCaseHandler.handle(params)

    editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text
