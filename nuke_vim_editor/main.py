
import pathlib
from importlib import import_module

from PySide2.QtWidgets import QMainWindow, QApplication, QPlainTextEdit

from .status_bar import status_bar
from .editor_modes import EDITOR_MODES

for module in pathlib.Path(__file__).parent.glob('handlers/*.py'):
    import_module(f'nuke_vim_editor.handlers.{module.stem}')


def read_sample():
    with open('sample.txt', 'r') as f:
        return f.read()


def main():
    app = QApplication([])
    font = app.font()
    font.setFamilies(['JetBrainsMono Nerd Font', 'Courier'])
    font.setPixelSize(25)
    app.setFont(font)

    window = QMainWindow()
    window.setGeometry(100, 100, 1000, 1000)

    editor = QPlainTextEdit()

    editor.setPlainText(read_sample())
    editor.setCursorWidth(editor.fontMetrics().width(' '))
    window.setCentralWidget(editor)

    status_bar.register(window.statusBar())
    window.statusBar().showMessage('NORMAL')

    pool = []
    for mode in EDITOR_MODES:
        _m = mode(editor)
        pool.append(_m)
        editor.installEventFilter(_m)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
