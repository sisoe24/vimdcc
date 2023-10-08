import re
from typing import Dict, List

from PySide2.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_normal_handler


@register_normal_handler
class CommandsHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, cursor: QTextCursor, key_sequence: str, modifiers: List[str], event: QKeyEvent):
        ...
