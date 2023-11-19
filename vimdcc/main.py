import logging
from typing import Any, Dict

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QLabel, QWidget, QCheckBox, QPushButton,
                               QVBoxLayout, QPlainTextEdit)

# TODO: Figure out a cleaner way to do this
# Dont' remove these imports, they are needed for the cache decorator
from .handlers import normal, missing
from .status_bar import _StatusBar, status_bar
from .utils.cache import cache
from .editor_modes import EDITOR_MODES

LOGGER = logging.getLogger('vim')
_EVENT_FILTERS: Dict[str, Any] = {}


class VimDCC(QWidget):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)

        self.editor = editor

        self.toggle_vim = QPushButton('Toggle Vim')
        self.toggle_vim.clicked.connect(self._on_toggle_vim)
        self.toggle_vim.setCheckable(True)

        self.clear_register = QPushButton('Clear Registers')
        self.clear_register.clicked.connect(self._on_clear_register)

        self.launch_on_startup = QCheckBox('Launch on Startup')

        self.vim_status = QLabel('Vim: OFF')

        layout = QVBoxLayout()
        layout.addWidget(QLabel('<h1>VimDcc</h1>'))
        layout.addWidget(self.vim_status)
        layout.addWidget(self.toggle_vim)
        layout.addWidget(self.clear_register)
        layout.addWidget(self.launch_on_startup)
        layout.addWidget(_StatusBar())
        layout.addStretch()
        self.setLayout(layout)

    @Slot()
    def _on_clear_register(self):
        LOGGER.debug('Clearing register')

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
            self.editor.setCursorWidth(2)

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
