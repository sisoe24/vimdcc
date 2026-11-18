import os
import json
import pathlib
from typing import Any
from dataclasses import field, fields, dataclass

SETTINGS_FILE = pathlib.Path(__file__).parent.parent / 'vimdcc.json'


def read_json(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: pathlib.Path, data: Any) -> None:
    # write to a temp file first: a crash mid-write must not corrupt the file
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=4))
    os.replace(tmp, path)


@dataclass
class VimDccSettings:
    launch_on_startup: bool = field(init=False, default=False)
    clipboard_size: int = field(init=False, default=100)
    previewer_auto_insert: bool = field(init=False, default=True)
    copy_to_system_clipboard: bool = field(init=False, default=True)

    def __post_init__(self):
        self._load_settings()

    def _load_settings(self):
        for key, value in read_json(SETTINGS_FILE).items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save_settings(self):
        write_json(SETTINGS_FILE, {f.name: getattr(self, f.name) for f in fields(self)})


Settings = VimDccSettings()
