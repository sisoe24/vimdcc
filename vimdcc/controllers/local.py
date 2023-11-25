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


class LocalVimDcc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(read_sample())

        self.vim_dcc = VimDCC(self.editor)

        layout = QVBoxLayout()
        layout.addWidget(self.vim_dcc)
        layout.addWidget(QLabel('<h1>Local VimDcc</h1>'))
        layout.addWidget(self.editor)
        layout.addWidget(self.vim_dcc.status_bar)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)

    font = app.font()
    # font.setFamilies(['Monaco', 'Courier'])
    # font.setPixelSize(25)
    app.setFont(font)

    set_theme(app)

    window = LocalVimDcc()
    window.setGeometry(100, 100, 1000, 1000)
    window.editor.setFocus()

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
