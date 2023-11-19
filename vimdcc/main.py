import logging
from typing import Any, Dict

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QLabel, QWidget, QCheckBox, QLineEdit,
                               QPushButton, QVBoxLayout, QPlainTextEdit)

from .handlers import normal, missing
from .registers import Registers
from .status_bar import status_bar
from .editor_modes import EDITOR_MODES

LOGGER = logging.getLogger('vim')
_EVENT_FILTERS: Dict[str, Any] = {}


class VimDCC(QWidget):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)

        self.editor = editor
        self.status_bar = QLineEdit()
        status_bar.register(self.status_bar)

        self.toggle_vim = QPushButton('Toggle Vim Mode')
        self.toggle_vim.clicked.connect(self._on_toggle_vim)
        self.toggle_vim.setCheckable(True)

        self.clear_register = QPushButton('Clear Registers')
        self.clear_register.clicked.connect(self._on_clear_register)

        self.launch_on_startup = QCheckBox('Launch on Startup')

        self.vim_status = QLabel('Vim: OFF')

        layout = QVBoxLayout()
        layout.addWidget(QLabel('<h1>VimDcc</h1>'))
        layout.addWidget(self.vim_status)
        layout.addWidget(self.launch_on_startup)
        layout.addWidget(self.toggle_vim)
        layout.addWidget(self.clear_register)
        layout.addWidget(self.status_bar)
        layout.addStretch()
        self.setLayout(layout)

    @Slot()
    def _on_clear_register(self):
        Registers.clear()

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
                _EVENT_FILTERS[f'{mode.__name__}_filter'] = event_filter

            LOGGER.debug(f'event_filter: {event_filter}')
            action(event_filter)

        self.editor.viewport().update()
