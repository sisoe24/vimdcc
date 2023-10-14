

from PySide2.QtWidgets import QPlainTextEdit

from ..handlers_core import BaseHandler, register_normal_handler
from .._types import EventParams


@register_normal_handler
class SomeCustomHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams) -> bool:
        print("Too lazy to handle :(")
        return False

    def should_handle(self, params: EventParams) -> bool:
        return False
