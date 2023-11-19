import json

from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout


class VimPreferencesModel:
    def __init__(self):
        self._settings = self.load()

    def load(self):
        with open('vimdcc.json') as f:
            return json.load(f)

    def save(self):
        with open('vimdcc.json', 'w') as f:
            json.dump(self._settings, f)


class VimPreferencesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('HELLO'))
        self.setLayout(layout)


class VimPreferencesController:
    def __init__(self, view: VimPreferencesView, model: VimPreferencesModel):
        self._view = view
        self._model = model


class VimPreferences:
    def __init__(self):
        self._model = VimPreferencesModel()
        self._view = VimPreferencesView()
        self._controller = VimPreferencesController(self._view, self._model)

    def view(self):
        return self._view

    def model(self):
        return self._model

    def controller(self):
        return self._controller
