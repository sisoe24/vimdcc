import logging
from typing import Any, Dict

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QLabel, QDialog, QWidget, QToolBar, QLineEdit,
                               QFormLayout, QMainWindow, QPushButton,
                               QVBoxLayout, QPlainTextEdit)

from .about import about
from .handlers import (  # DONT REMOVE THIS LINE (needed for loading) FIXME
    normal, missing)
from .settings import Settings
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
        gitrepo = 'https://github.com/sisoe24/vimdcc'
        links = {
            'issues': f'{gitrepo}/issues',
            'changelog': f'{gitrepo}/blob/master/CHANGELOG.md',
            'readme': f'{gitrepo}/blob/master/README.md'
        }
        import webbrowser
        webbrowser.open(links[link.lower()])


class VimDCC(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_bar = QLineEdit()
        self.status_bar.setObjectName('vimdcc_status_bar')

        status_bar.register(self.status_bar)

        self.toggle_vim = QPushButton('Toggle Vim Mode')
        self.toggle_vim.setCheckable(True)
        self.toggle_vim.clicked.connect(self._on_toggle_vim)

        self.vim_status = QLabel('<h3>Vim: OFF</h3>')
        self.vim_status.setAlignment(Qt.AlignCenter)

        self.preferences = VimPreferences()
        if Settings.launch_on_startup:
            self.toggle_vim.setChecked(True)
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
        self.addToolBar(toolbar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def register_events(self) -> Any:
        raise NotImplementedError('register_events must be implemented in subclass')

    def get_editor(self) -> QPlainTextEdit:
        """Get the editor to install the event filters on.

        This method acts as an abstractmethod and must be implemented in a subclass.

        """
        raise NotImplementedError('get_editor must be implemented in subclass')

    @Slot(bool)
    def _on_toggle_vim(self, checked: bool):

        input_editor = self.get_editor()

        if checked:
            LOGGER.debug('Turning Vim ON')
            input_editor.setCursorWidth(input_editor.fontMetrics().width(' '))
            self.vim_status.setText('<h3>Vim: ON</h3>')
            filter_event = input_editor.installEventFilter
        else:
            LOGGER.debug('Turning Vim OFF')
            self.vim_status.setText('<h3>Vim: OFF</h3>')
            filter_event = input_editor.removeEventFilter
            input_editor.setCursorWidth(2)

        for mode in EDITOR_FILTERS:
            LOGGER.debug(f'Installing: {mode.__name__}')

            if _EVENT_FILTERS.get(f'{mode.__name__}_filter'):
                event_filter = _EVENT_FILTERS[f'{mode.__name__}_filter']
            else:
                event_filter = mode(input_editor)
                _EVENT_FILTERS[f'{mode.__name__}_filter'] = event_filter

            LOGGER.debug(f'event_filter: {event_filter}')
            filter_event(event_filter)

        input_editor.viewport().update()
