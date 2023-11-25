import json
import pathlib
from dataclasses import field, fields, dataclass

SETTINGS_FILE = pathlib.Path(__file__).parent.parent / 'vimdcc.json'
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text('{}')


@dataclass
class VimDccSettings:
    launch_on_startup: bool = field(init=False, default=False)
    clipboard_size: int = field(init=False, default=100)
    install_to_all_editors: bool = field(init=False, default=False)
    previewer_auto_insert: bool = field(init=False, default=True)
    copy_to_system_clipboard: bool = field(init=False, default=True)

    def __post_init__(self):
        self._load_settings()

    def _load_settings(self):
        with SETTINGS_FILE.open() as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def save_settings(self):
        data = {field.name: getattr(self, field.name) for field in fields(self)}
        with SETTINGS_FILE.open('w') as f:
            json.dump(data, f, indent=4)


Settings = VimDccSettings()
