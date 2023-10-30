"""Keeping track of missing Vim commands that I would like to implement."""
from PySide2.QtWidgets import QPlainTextEdit

from ..handler_base import BaseHandler, register_normal_handler
from ..handler_parameters import HandlerParams


@register_normal_handler
class MissingHandler(BaseHandler):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)

    def handle(self, params: HandlerParams):

        missing = [
            'p', 'P', 'u', 'U', 'r', 'R', '<<', '>>', 'W', 'E', 'B', '.', 'zz',
        ]

        key_sequence = params.keys
        if key_sequence in missing:
            print(f'Not implemented yet: {key_sequence}')
            params.status_bar.emit('NORMAL', f'Not implemented yet: {key_sequence}')
            return True

        return False
