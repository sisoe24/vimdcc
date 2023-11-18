from typing import Optional

from PySide2.QtWidgets import QStatusBar


class StatusBar:
    status_bar: Optional[QStatusBar] = None

    @classmethod
    def register(cls, status_bar: QStatusBar):
        cls.status_bar = status_bar

    @classmethod
    def emit(cls, mode: str, keys: str):
        if not cls.status_bar:
            return
        cls.status_bar.showMessage(f'{mode} {keys}')

    @classmethod
    def get_text(cls):
        return cls.status_bar.currentMessage() if cls.status_bar else ''


status_bar = StatusBar()
