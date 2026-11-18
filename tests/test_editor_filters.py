import pytest
from pytestqt.qtbot import QtBot

from vimdcc.events import EventManager
from vimdcc.editor_mode import Modes, EditorMode
from vimdcc.editor_filters import NormalEventFilter

from vimdcc._qt import Qt, QEvent, QKeyEvent, QPlainTextEdit


@pytest.fixture()
def vim(qtbot: QtBot) -> NormalEventFilter:
    editor = QPlainTextEdit()
    editor.setPlainText('one\ntwo\nthree')
    EditorMode.mode = Modes.NORMAL
    return NormalEventFilter(editor)


def press(vim: NormalEventFilter, key: int, text: str = '', mods=Qt.NoModifier):
    vim.parse_keys(vim.editor, QKeyEvent(QEvent.KeyPress, key, mods, text))


def line(vim: NormalEventFilter) -> int:
    return vim.editor.textCursor().blockNumber()


def test_backspace_removes_pending_key(vim: NormalEventFilter):
    press(vim, Qt.Key_G, 'g')
    press(vim, Qt.Key_Backspace, '\x08')
    assert vim.key_sequence == ''

    press(vim, Qt.Key_J, 'j')
    assert line(vim) == 1


def test_ctrl_r_does_not_block_next_key(vim: NormalEventFilter):
    calls = []

    def run():
        calls.append(1)

    EventManager.register('execute_code', run)
    press(vim, Qt.Key_R, '\x12', Qt.ControlModifier)
    EventManager.unregister('execute_code', run)

    assert calls == [1]
    press(vim, Qt.Key_J, 'j')
    assert line(vim) == 1
