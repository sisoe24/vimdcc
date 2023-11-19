import json
import pathlib
from typing import Any, Dict

SETTINGS_FILE = pathlib.Path(__file__).parent.parent / 'vimdcc.json'
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text('{}')

SettingsDict = Dict[str, Any]


def _load_settings() -> SettingsDict:
    with SETTINGS_FILE.open() as f:
        return json.load(f)


def _save_settings(settings: SettingsDict):
    with SETTINGS_FILE.open('w') as f:
        json.dump(settings, f)


class _VimDccSettings():
    def __init__(self):
        self._settings = _load_settings()

    def get(self, key: str, default: Any = None):
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        self._settings[key] = value
        _save_settings(self._settings)


Settings = _VimDccSettings()
