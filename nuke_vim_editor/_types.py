from enum import Enum, auto
from typing import Any, Callable

from PySide2.QtWidgets import QPlainTextEdit

NormalModeHandlerType = Callable[[QPlainTextEdit], Any]

class Modes(str, Enum):
    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()
    COMMAND = auto()
    MARKS = auto()
