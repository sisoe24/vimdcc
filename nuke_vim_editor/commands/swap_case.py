from typing import Literal

from PySide2.QtWidgets import QPlainTextEdit

from ..command_base import BaseCommand
from ..handler_parameters import HandlerParams

SwapMode = Literal['swapcase', 'upper', 'lower']


def create_swap_case_command(mode: SwapMode):
    class SwapCaseCommand(BaseCommand):
        def __init__(self, editor: QPlainTextEdit, mode: str):
            self.editor = editor
            self.mode = mode

        def execute(self, params: HandlerParams):
            cursor = params.cursor
            text = cursor.selectedText()
            cursor.removeSelectedText()
            cursor.insertText(getattr(text, mode)())
            return True

    return SwapCaseCommand


SwapCase = create_swap_case_command('swapcase')
SwapLower = create_swap_case_command('lower')
SwapUpper = create_swap_case_command('upper')
