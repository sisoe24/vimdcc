
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QLabel, QWidget, QCheckBox, QMessageBox,
                               QVBoxLayout)

from .settings import Settings, _VimDccSettings


class VimPreferencesModel:
    def __init__(self, settings: _VimDccSettings):
        self._settings = settings

    def set_launch_on_startup(self, value: bool):
        self._settings.set('launch_on_startup', value)

    def launch_on_startup(self) -> bool:
        return self._settings.get('launch_on_startup', False)


class VimPreferencesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.launch_on_startup = QCheckBox('Launch on Startup')

        layout = QVBoxLayout()
        layout.addWidget(self.launch_on_startup)
        self.setLayout(layout)


class VimPreferencesController:
    def __init__(self, view: VimPreferencesView, model: VimPreferencesModel):
        self._view = view
        self._model = model

        self._view.launch_on_startup.stateChanged.connect(self._on_launch_on_startup)

    @Slot(int)
    def _on_launch_on_startup(self, state: int):
        QMessageBox.information(
            self._view, 'VimDcc', 'You must restart VimDcc for this change to take effect.'
        )
        self._model.set_launch_on_startup(state == 2)

    def init(self):
        widget = self._view.launch_on_startup
        widget.blockSignals(True)
        widget.setChecked(self._model.launch_on_startup())
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
