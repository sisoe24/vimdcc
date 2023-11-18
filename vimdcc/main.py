
import logging
import pathlib
from typing import Any, Dict
from importlib import import_module

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QLabel, QWidget, QPushButton, QVBoxLayout,
                               QPlainTextEdit)

from .status_bar import status_bar
from .utils.cache import cache
from .editor_modes import EDITOR_MODES

for module in pathlib.Path(__file__).parent.glob('handlers/*.py'):
    import_module(f'nuke_vim_editor.handlers.{module.stem}')

LOGGER = logging.getLogger('vim')
_EVENT_FILTERS: Dict[str, Any] = {}


class VimDCC(QWidget):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)

        self.editor = editor

        self.toggle_vim = QPushButton('Toggle Vim')
        self.toggle_vim.clicked.connect(self._on_toggle_vim)
        self.toggle_vim.setCheckable(True)

        self.vim_status = QLabel('Vim: OFF')

        layout = QVBoxLayout()
        layout.addWidget(QLabel('<h1>VimLite</h1>'))
        layout.addWidget(self.vim_status)
        layout.addWidget(self.toggle_vim)
        self.setLayout(layout)

    @Slot(bool)
    def _on_toggle_vim(self, checked: bool):

        if checked:
            LOGGER.debug('Turning Vim ON')
            self.editor.setCursorWidth(self.editor.fontMetrics().width(' '))
            self.vim_status.setText('Vim: ON')
            action = self.editor.installEventFilter
        else:
            LOGGER.debug('Turning Vim OFF')
            self.vim_status.setText('Vim: OFF')
            action = self.editor.removeEventFilter

        for mode in EDITOR_MODES:
            LOGGER.debug(f'Installing: {mode.__name__}')

            if _EVENT_FILTERS.get(f'{mode.__name__}_filter'):
                event_filter = _EVENT_FILTERS[f'{mode.__name__}_filter']
            else:
                event_filter = mode(self.editor)

            # The event filters get garbage collected if we don't keep a
            # reference to them
            _EVENT_FILTERS[f'{mode.__name__}_filter'] = event_filter

            LOGGER.debug(f'event_filter: {event_filter}')
            action(event_filter)

        self.editor.viewport().update()
