import contextlib
from typing import Optional

import nukescripts
from PySide2.QtWidgets import QWidget, QSplitter, QApplication, QPlainTextEdit

from ...utils.cache import cache


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


with contextlib.suppress(ImportError):
    nukescripts.panels.registerWidgetAsPanel(
        'NukeVimLite', 'NukeVimLite', 'uk.co.thefoundry.NukeVimLite'
    )
