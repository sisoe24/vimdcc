from PySide2.QtWidgets import QPlainTextEdit

from .._types import EventParams
from ..status_bar import status_bar
from ..handlers_core import BaseHandler, register_normal_handler


@register_normal_handler
class MissingHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: EventParams):

        missing = [
            'p', 'P', 'u', 'U', 'r', 'R', '<<', '>>', 'W', 'E', 'B', '.', 'zz',
        ]

        key_sequence = params.keys
        if key_sequence in missing:
            print(f'Not implemented yet: {key_sequence}')
            status_bar.emit('NORMAL', f'Not implemented yet: {key_sequence}')
            return True

        return False
