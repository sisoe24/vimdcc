import os
import sys
import pathlib
import contextlib
from typing import Optional

from PySide2.QtWidgets import QWidget, QSplitter, QApplication, QPlainTextEdit

from ..main import VimDCC
from ..utils import cache


@cache
def get_script_editor() -> Optional[QWidget]:
    return next(
        (
            widget
            for widget in QApplication.allWidgets()
            if 'scripteditor.1' in widget.objectName()
        ),
        None,
    )


@cache
def get_console() -> Optional[QWidget]:
    script_editor = get_script_editor()
    return script_editor.findChild(QSplitter) if script_editor else None


@cache
def get_console_editor() -> Optional[QPlainTextEdit]:
    console = get_console()
    input_editor = console.findChild(QPlainTextEdit)
    return input_editor or None


class NukeVimDCC(VimDCC):
    def __init__(self, parent=None):
        super().__init__(get_console_editor(), parent)


def install_nuke_vim():
    # sys.path.append(os.path.dirname(__file__))
    sys.path.append(str(pathlib.Path(__file__).parent.parent))
    with contextlib.suppress(ImportError):
        import nukescripts
        nukescripts.panels.registerWidgetAsPanel(
            'vimdcc.controllers.install_nuke.NukeVimDCC', 'NukeVimDCC',
            'uk.co.thefoundry.NukeVimDCC'
        )
