

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_handler


@register_handler
class SomeCustomHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, event: QKeyEvent):
        print("Too lazy to handle :(")

    def should_handle(self, cursor: QTextCursor, event: QKeyEvent) -> bool:
        return False
