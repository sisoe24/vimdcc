

from typing import List

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_normal_handler


@register_normal_handler
class SomeCustomHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent) -> bool:
        print("Too lazy to handle :(")
        return False

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent, key_sequence: str) -> bool:
        return False
