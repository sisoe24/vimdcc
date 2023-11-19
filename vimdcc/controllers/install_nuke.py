import os
import sys
import pathlib
import contextlib
from typing import Optional

from PySide2.QtWidgets import (QLabel, QWidget, QLineEdit, QSplitter,
                               QVBoxLayout, QApplication, QPlainTextEdit)

from ..main import VimDCC
from ..utils import cache


@cache
def get_script_editor() -> QPlainTextEdit:
    for widget in QApplication.allWidgets():
        if 'scripteditor.1' in widget.objectName():
            return widget
    raise RuntimeError('Could not find script editor')


@cache
def get_console() -> QSplitter:
    return get_script_editor().findChild(QSplitter)


@cache
def get_console_editor() -> QPlainTextEdit:
    input_editor = get_console().findChild(QPlainTextEdit)
    if not input_editor:
        raise RuntimeError('Could not find input editor')
    return input_editor


class NukeVimDCC(VimDCC):
    def __init__(self, parent=None):
        super().__init__(get_console_editor(), parent)

        self.console = get_console()

    # def load_status_bar(self):
    #     if not 'shoudl_load':
    #         return

    #     self.console.addWidget(self.status_bar)
    #     self.console.setStretchFactor(0, 1)  # First textEdit takes up maximum space
    #     self.console.setStretchFactor(1, 1)  # Second textEdit takes up maximum space
    #     self.console.setStretchFactor(2, 0)  # lineEdit takes up minimum space


def install_nuke_vim():
    with contextlib.suppress(ImportError):
        import nukescripts
        nukescripts.panels.registerWidgetAsPanel(
            'vimdcc.controllers.install_nuke.NukeVimDCC', 'NukeVimDCC',
            'uk.co.thefoundry.NukeVimDCC'
        )
