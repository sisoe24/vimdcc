
import contextlib
from functools import lru_cache

from .._qt import QWidget, QSplitter, QPushButton, QApplication, QPlainTextEdit

from ..main import VimDCC
from ..about import about
from ..events import EventManager
from ..settings import Settings


@lru_cache(maxsize=None)
def get_script_editor() -> QWidget:
    for widget in QApplication.allWidgets():
        if 'scripteditor.1' in widget.objectName():
            return widget
    raise RuntimeError('Could not find script editor')


@lru_cache(maxsize=None)
def get_splitter() -> QSplitter:
    return get_script_editor().findChild(QSplitter)


@lru_cache(maxsize=None)
def get_input_editor() -> QPlainTextEdit:
    input_editor = get_splitter().findChild(QPlainTextEdit)
    if not input_editor:
        raise RuntimeError('Could not find input editor')
    return input_editor


@lru_cache(maxsize=None)
def get_run_button() -> QWidget:
    # naively assume that the button always exists
    return next(
        (
            button
            for button in get_script_editor().findChildren(QPushButton)
            if button.toolTip().lower().startswith('run the current script')
        ),
        None,
    )


def _run_script():
    button = get_run_button()
    if button:
        button.click()


class NukeVimDCC(VimDCC):
    def __init__(self):
        super().__init__()

        self.splitter = get_splitter()
        self.load_status_bar()

        print(f'\nVimDCC loaded: NukeVimDCC {about()["version"]}\n')

    def get_editor(self) -> QPlainTextEdit:
        return get_input_editor()

    def load_status_bar(self):
        if not Settings.launch_on_startup:
            return

        # if vimdcc is automatically launched, the status bar is already loaded
        # but if the plugin is not visible in the ui, loading the plugin will
        # load a new status bar. We need to remove the old one and replace it
        if self.splitter.findChild(QWidget, 'vimdcc_status_bar'):
            self.splitter.replaceWidget(2, self.status_bar)
            return

        self.splitter.addWidget(self.status_bar)
        self.splitter.setStretchFactor(0, 1)  # First textEdit takes up maximum space
        self.splitter.setStretchFactor(1, 1)  # Second textEdit takes up maximum space
        self.splitter.setStretchFactor(2, 0)  # status bar takes up minimum space


def install_nuke():
    # register here, not in NukeVimDCC.__init__: Nuke creates a new panel
    # instance every time the panel opens
    EventManager.register('execute_code', _run_script)

    with contextlib.suppress(ImportError):
        import nukescripts
        nukescripts.panels.registerWidgetAsPanel(
            'vimdcc.controllers.install_nuke.NukeVimDCC', 'NukeVimDCC',
            'uk.co.thefoundry.NukeVimDCC'
        )
