
import pathlib
from importlib import import_module

from PySide2.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QApplication,
                               QPlainTextEdit)

from .status_bar import status_bar
from .editor_modes import InsertMode, NormalMode, CommandMode, VisualLineMode
from .handlers_core import get_normal_handlers

for module in pathlib.Path(__file__).parent.glob("handlers/*.py"):
    import_module(f'nuke_vim_editor.handlers.{module.stem}')


# TODO: Jump to line
# TODO: undo/redo
# TODO: Highlighting


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

    status_bar.register(window.statusBar())
    window.statusBar().showMessage("NORMAL")

    normal_mode = NormalMode(editor, get_normal_handlers())
    editor.installEventFilter(normal_mode)

    insert_mode = InsertMode(editor)
    editor.installEventFilter(insert_mode)

    command_mode = CommandMode(editor)
    editor.installEventFilter(command_mode)

    visual_mode = VisualLineMode(editor)
    editor.installEventFilter(visual_mode)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
