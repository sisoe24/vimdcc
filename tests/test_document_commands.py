from typing import List, cast
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.editor_modes import Modes
from nuke_vim_editor.handlers.normal import DocumentHandler
from nuke_vim_editor.handler_parameters import HandlerParams


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
    position = cursor.position()

    assert editor.toPlainText()[position] == data.expected_text
    assert cursor.position() == data.expected_pos
    assert cursor.anchor() == data.expected_pos
    assert cursor.hasSelection() is False
    assert not cursor.selectedText()


# paragraph separator
P = '\u2029'


@pytest.mark.parametrize('data', [
    MotionTest(['gg'], 'foo\nbar\nfoo\nbar', 7, f'foo{P}bar', 0),
    MotionTest(['G'], 'foo\nbar', 0, f'foo{P}bar', 14),
    MotionTest(['}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, f'foo{P}', 4),
    MotionTest(['}', '}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, f'foo{P}{P}bar{P}', 9),
    MotionTest(['{', '{'], 'foo\n\nbar\n\nfoo\n\nbar', 8, f'foo{P}{P}bar', 4),
])
def test_move_document_selection(handler: DocumentHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.VISUAL
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    cursor = editor.textCursor()

    assert cursor.hasSelection() is True
    assert cursor.selectedText() == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['c', 'gg'], 'foo\nbar', 7, '', 0),
    MotionTest(['c', 'G'], 'foo\nbar', 0, '', 0),
    MotionTest(['c', '}'], 'foo\n\nbar', 0, '\nbar', 0),
    MotionTest(['c', '}', '}'], 'foo\n\nbar', 0, '', 0),
    MotionTest(['c', '{', ], 'foo\n\nbar', 8, 'foo\n', 0),
    MotionTest(['c', '{', '{'], 'foo\n\nbar', 8, '', 0),
])
def test_move_document_edit(handler: DocumentHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.CHANGE
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['c', 'gg'], 'foo\nbar', 7, '', 0),
    MotionTest(['c', 'G'], 'foo\nbar', 0, '', 0),
    MotionTest(['c', '}'], 'foo\n\nbar', 0, '\nbar', 0),
    MotionTest(['c', '}', '}'], 'foo\n\nbar', 0, '', 0),
    MotionTest(['c', '{', ], 'foo\n\nbar', 8, 'foo\n', 0),
    MotionTest(['c', '{', '{'], 'foo\n\nbar', 8, '', 0),
])
def test_move_document_delete(handler: DocumentHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.DELETE
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    assert editor.toPlainText() == data.expected_text


@pytest.mark.parametrize('data', [
    MotionTest(['gg'], 'foo\nbar\nfoo\nbar', 7, f'foo{P}bar', 0),
    MotionTest(['G'], 'foo\nbar', 0, f'foo{P}bar', 14),
    MotionTest(['}'], 'foo\n\nbar\n\nfoo\n\nbar', 0, f'foo{P}', 4),
    MotionTest(['{'], 'foo\n\nbar\n\nfoo\n\nbar', 8, f'{P}bar', 4),
])
def test_move_document_yank(handler: DocumentHandler, data: MotionTest) -> None:
    editor = handler.editor
    editor.setPlainText(data.text)

    params = HandlerParams(
        cursor=editor.textCursor(),
        keys='',
        modifiers=[],
        event=None,
        mode=Modes.YANK
    )

    params.cursor.setPosition(data.cursor_start)

    for motion in data.motion:
        params.keys = motion
        handler.handle(params)
        editor.setTextCursor(params.cursor)

    register = handler.registers.get_register('numbered')
    assert register[0] == data.expected_text
