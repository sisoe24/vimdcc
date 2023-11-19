from typing import Optional

from PySide2.QtWidgets import QLineEdit


class StatusBar:
    status_bar: Optional[QLineEdit] = None

    @classmethod
    def register(cls, status_bar: QLineEdit):
        cls.status_bar = status_bar
        cls.status_bar.setReadOnly(True)

    @classmethod
    def write(cls, mode: str, keys: str):
        if not cls.status_bar:
            return
        cls.status_bar.setText(f"{mode} {keys}")

    @classmethod
    def get_text(cls) -> str:
        return cls.status_bar.text() if cls.status_bar else ''


status_bar = StatusBar()
