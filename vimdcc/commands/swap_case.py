from enum import Enum

from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import BaseCommand
from ..handler_parameters import HandlerParams


class SwapMode(str, Enum):
    SWAPCASE = 'swapcase'
    LOWER = 'lower'
    UPPER = 'upper'


def create_swap_case_command(mode: SwapMode):
    class SwapCaseCommand(BaseCommand):
        def __init__(self, editor: QPlainTextEdit):
            self.editor = editor

        def execute(self, params: HandlerParams):
            cursor = params.cursor
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(getattr(text, mode)())
            return True

    return SwapCaseCommand


SwapCase = create_swap_case_command(SwapMode.SWAPCASE)
SwapLower = create_swap_case_command(SwapMode.LOWER)
SwapUpper = create_swap_case_command(SwapMode.UPPER)
