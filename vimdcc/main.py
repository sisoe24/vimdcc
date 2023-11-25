import logging
from typing import Any, Dict

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QLabel, QDialog, QWidget, QToolBar, QLineEdit,
                               QFormLayout, QMainWindow, QPushButton,
                               QVBoxLayout, QPlainTextEdit)

from .about import about
from .handlers import normal, missing
from .settings import Settings
from .registers import Registers
from .status_bar import status_bar
from .preferences import VimPreferences
from .editor_filters import EDITOR_FILTERS

LOGGER = logging.getLogger('vim')
_EVENT_FILTERS: Dict[str, Any] = {}


class HelpWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('VimDcc Help')

        form_layout = QFormLayout()
        for name, value in about().items():
            form_layout.addRow(f'{name.title()}:', QLabel(value))

        self.issues = self._button_factory('Issues')
        self.readme = self._button_factory('Readme')
        self.changelog = self._button_factory('Changelog')

        form_layout.addRow(self.readme)
        form_layout.addRow(self.changelog)
        form_layout.addRow(self.issues)
        self.setLayout(form_layout)

    def _button_factory(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(lambda: self._on_open_link(text))
        return button

    @Slot(str)
    def _on_open_link(self, link: str):
        print('TODO: open link', link)
        gitrepo = 'https://github.com/sisoe24/vimdcc'
        links = {
            'issues': '',
            'changelog': '',
            'readme': ''
        }
        import webbrowser
        webbrowser.open(links[link.lower()])


class VimDCC(QMainWindow):
    def __init__(self, editor: QPlainTextEdit, parent=None):
        super().__init__(parent)

        self.editor = editor
        self.status_bar = QLineEdit()
        status_bar.register(self.status_bar)

        self.toggle_vim = QPushButton('Toggle Vim Mode')
        self.toggle_vim.setCheckable(True)
        self.toggle_vim.clicked.connect(self._on_toggle_vim)

        self.clear_register = QPushButton('Clear Registers')
        self.clear_register.clicked.connect(self._on_clear_register)

        self.vim_status = QLabel('Vim: OFF')
        self.vim_status.setAlignment(Qt.AlignCenter)

        self.preferences = VimPreferences()
        if Settings.launch_on_startup:
            self._on_toggle_vim(True)

        main_label = QLabel('<h1>VimDcc</h1>')
        main_label.setAlignment(Qt.AlignCenter)

        preference_label = QLabel('<h2>Preferences</h2>')

        layout = QVBoxLayout()
        layout.addWidget(main_label)
        layout.addWidget(self.vim_status)
        layout.addWidget(self.toggle_vim)
        layout.addWidget(preference_label)
        layout.addWidget(self.preferences.view())
        layout.addWidget(self.status_bar)
        layout.addStretch()

        toolbar = QToolBar()
        toolbar.addAction('Help', HelpWidget(self).show)
        toolbar.addAction('Clear Register', self._on_clear_register)
        self.addToolBar(toolbar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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

        for mode in EDITOR_FILTERS:
            LOGGER.debug(f'Installing: {mode.__name__}')

            if _EVENT_FILTERS.get(f'{mode.__name__}_filter'):
                event_filter = _EVENT_FILTERS[f'{mode.__name__}_filter']
            else:
                event_filter = mode(self.editor)
                _EVENT_FILTERS[f'{mode.__name__}_filter'] = event_filter

            LOGGER.debug(f'event_filter: {event_filter}')
            action(event_filter)

        self.editor.viewport().update()
