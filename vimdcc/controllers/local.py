import sys

from PySide2.QtWidgets import (QLabel, QWidget, QMainWindow, QVBoxLayout,
                               QApplication, QPlainTextEdit)

from ..main import VimDCC
from ..utils.theme import set_theme


def read_sample(debug=False):
    s = ''
    with open('sample.txt', 'r') as f:
        if debug:
            content = f.read()
            for i in content:
                s += repr(i) + '\n' if i in ['\n', '\t', '\r'] else i
            return s
        return f.read()


class LocalVimDcc(VimDCC):
    def __init__(self):
        # create the editor before calling super().__init__()
        # otherwise the editor will not be available in the super class
        # if the launch_on_startup is True
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(read_sample())

        super().__init__()

    def get_editor(self) -> QPlainTextEdit:
        return self.editor


class LocalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vim_dcc = LocalVimDcc()

        layout = QVBoxLayout()
        layout.addWidget(self.vim_dcc)
        layout.addWidget(QLabel('<h1>Local VimDcc</h1>'))
        layout.addWidget(self.vim_dcc.editor)
        layout.addWidget(self.vim_dcc.status_bar)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)

    font = app.font()
    font.setFamilies(['Monaco', 'Courier'])
    font.setPixelSize(25)
    app.setFont(font)

    set_theme(app)

    window = LocalWidget()
    window.setGeometry(100, 100, 1000, 1000)
    window.vim_dcc.editor.setFocus()

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
