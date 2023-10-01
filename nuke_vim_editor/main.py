from __future__ import annotations

import pathlib
from typing import cast
from importlib import import_module

from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt, QEvent, QObject
from PySide2.QtWidgets import QMainWindow, QApplication, QPlainTextEdit

from .editor_modes import Modes, EditorMode
from .handlers_core import get_handlers

for module in pathlib.Path(__file__).parent.glob("handlers/*.py"):
    import_module(f'nuke_vim_editor.handlers.{module.stem}')


# TODO: Add options for arrow keys
# TODO: Add options for removing mouse
# TODO: Jump to line
# TODO: undo/redo
# TODO: Highlighting


class VimNormalMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()

        self._editor = editor
        self._handlers = [handler(self._editor) for handler in get_handlers()]

    def eventFilter(self, watched: QObject, event: QEvent):
        if not isinstance(watched, QPlainTextEdit):
            return False

        if EditorMode.mode == Modes.INSERT:
            return False

        if event.type() == QEvent.KeyPress:
            cursor = watched.textCursor()
            for handler in self._handlers:
                if handler.should_handle(cursor, cast(QKeyEvent, event)):
                    handler.handle(cursor, cast(QKeyEvent, event))
            watched.setTextCursor(cursor)
            return True

        return False


class VimInsertMode(QObject):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__()
        self.editor = editor

    def eventFilter(self, watched: QObject, event):

        if EditorMode.mode == Modes.NORMAL:
            return False

        if (
            event.type() == QEvent.KeyPress and
            (event.key() == Qt.Key_Escape and EditorMode.mode == Modes.INSERT)
        ):
            self.editor.setCursorWidth(self.editor.fontMetrics().width(" "))
            EditorMode.mode = Modes.NORMAL
            return True
        return False


sampletext = '''
import random

def main(name):
    print(f"Hello {name}!")

for i in range(10):
    if i % 2 == 0:
        main("world")
    else:
        main("universe")
'''.lstrip()


def main():
    app = QApplication([])
    font = app.font()
    font.setFamilies(["JetBrainsMono Nerd Font", "Courier"])
    font.setPixelSize(30)
    app.setFont(font)

    window = QMainWindow()
    window.setGeometry(100, 100, 800, 600)

    editor = QPlainTextEdit()

    editor.setPlainText(sampletext)
    editor.setCursorWidth(editor.fontMetrics().width(" "))
    window.setCentralWidget(editor)

    normal_mode = VimNormalMode(editor)
    editor.installEventFilter(normal_mode)

    insert_mode = VimInsertMode(editor)
    editor.installEventFilter(insert_mode)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
