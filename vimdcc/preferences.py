
from typing import Any

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QFrame, QSpinBox, QCheckBox, QFormLayout,
                               QMessageBox)

from .settings import Settings, VimDccSettings


class VimPreferencesModel:
    def __init__(self, settings: VimDccSettings):
        self.settings = settings

    def set(self, key: str, value: Any):
        if not hasattr(self.settings, key):
            raise ValueError(f'Invalid key: {key}')

        setattr(self.settings, key, value)
        self.settings.save_settings()


class VimPreferencesView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet('QFrame {background-color: #3B3B3B;}')

        self.launch_on_startup = QCheckBox()
        self.copy_to_system_clipboard = QCheckBox()

        self.clipboard_size = QSpinBox()
        self.clipboard_size.setRange(1, 1000)
        self.clipboard_size.setSingleStep(1)
        self.clipboard_size.setValue(100)

        self.previewer_auto_insert = QCheckBox()
        self.previewer_auto_insert.setChecked(True)

        self.install_to_all_editors = QCheckBox()

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        form_layout.addRow('Launch on Startup', self.launch_on_startup)
        form_layout.addRow('Install to all editors', self.install_to_all_editors)
        form_layout.addRow('Previewer auto insert', self.previewer_auto_insert)
        form_layout.addRow('Clipboard Size', self.clipboard_size)
        form_layout.addRow('Copy to system clipboard', self.copy_to_system_clipboard)

        self.setLayout(form_layout)


class VimPreferencesController:
    def __init__(self, view: VimPreferencesView, model: VimPreferencesModel):
        self._view = view
        self._model = model

        self._view.launch_on_startup.stateChanged.connect(self._on_launch_on_startup)
        self._view.clipboard_size.valueChanged.connect(self._on_clipboard_size)
        self._view.previewer_auto_insert.stateChanged.connect(self._on_previewer_auto_insert)
        self._view.copy_to_system_clipboard.stateChanged.connect(self._on_copy_to_system_clipboard)

    @Slot(int)
    def _on_copy_to_system_clipboard(self, state: int):
        self._model.set('copy_to_system_clipboard', state == 2)

    @Slot(int)
    def _on_previewer_auto_insert(self, state: int):
        self._model.set('previewer_auto_insert', state == 2)

    @Slot(int)
    def _on_clipboard_size(self, value: int):
        self._model.set('clipboard_size', value)

    @Slot(int)
    def _on_launch_on_startup(self, state: int):
        QMessageBox.information(
            self._view, 'VimDcc', 'You must restart VimDcc for this change to take effect.'
        )
        self._model.set('launch_on_startup', state == 2)

    def init(self):

        settings = self._model.settings

        self._view.copy_to_system_clipboard.setChecked(settings.copy_to_system_clipboard)
        self._view.previewer_auto_insert.setChecked(settings.previewer_auto_insert)
        self._view.clipboard_size.setValue(settings.clipboard_size)

        widget = self._view.launch_on_startup
        widget.blockSignals(True)
        widget.setChecked(settings.launch_on_startup)
        widget.blockSignals(False)


class VimPreferences:
    def __init__(self):
        self._model = VimPreferencesModel(Settings)
        self._view = VimPreferencesView()
        self._controller = VimPreferencesController(self._view, self._model)
        self._controller.init()

    def view(self):
        return self._view

    def model(self):
        return self._model

    def controller(self):
        return self._controller
