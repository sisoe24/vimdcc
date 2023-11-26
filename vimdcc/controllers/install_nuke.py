
import contextlib
from typing import Tuple

from PySide2.QtWidgets import QWidget, QSplitter, QApplication, QPlainTextEdit

from ..main import VimDCC
from ..utils import cache
from ..settings import Settings


@cache
def get_script_editor() -> QWidget:
    for widget in QApplication.allWidgets():
        if 'scripteditor.1' in widget.objectName():
            return widget
    raise RuntimeError('Could not find script editor')


@cache
def get_splitter() -> QSplitter:
    return get_script_editor().findChild(QSplitter)


@cache
def get_input_editor() -> QPlainTextEdit:
    input_editor = get_splitter().findChild(QPlainTextEdit)
    if not input_editor:
        raise RuntimeError('Could not find input editor')
    return input_editor


class NukeVimDCC(VimDCC):
    def __init__(self):
        super().__init__()

        self.splitter = get_splitter()
        self.load_status_bar()

    def get_editor(self) -> QPlainTextEdit:
        return get_input_editor()

    def load_status_bar(self):
        if not Settings.launch_on_startup:
            return

        self.splitter.addWidget(self.status_bar)
        self.splitter.setStretchFactor(0, 1)  # First textEdit takes up maximum space
        self.splitter.setStretchFactor(1, 1)  # Second textEdit takes up maximum space
        self.splitter.setStretchFactor(2, 0)  # lineEdit takes up minimum space


def install_nuke():
    with contextlib.suppress(ImportError):
        import nukescripts
        nukescripts.panels.registerWidgetAsPanel(
            'vimdcc.controllers.install_nuke.NukeVimDCC', 'NukeVimDCC',
            'uk.co.thefoundry.NukeVimDCC'
        )
