import random
from enum import Enum, auto

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtCore import Qt, QEvent, QObject
from PySide2.QtWidgets import (QWidget, QLineEdit, QSplitter, QTextEdit,
                               QPushButton, QVBoxLayout, QApplication,
                               QPlainTextEdit)


def get_script_editor():
    se = None
    for widget in QApplication.allWidgets():
        if 'scripteditor.1' in widget.objectName():
            se = widget
    return se


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_bar = QLineEdit()
        self.status_bar.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        self.setLayout(layout)


script_editor = get_script_editor()

console = script_editor.findChild(QSplitter)
console.addWidget(StatusBar())

input = script_editor.findChild(QPlainTextEdit)
input.setPlainText("nuke.createNode('Read')")


input.setCursorWidth(10)

input.setPlainText(f'{random.random()}')
input.appendPlainText(f'{random.random()}')
input.appendPlainText(f'{random.random()}')
