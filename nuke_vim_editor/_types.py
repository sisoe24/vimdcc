from enum import Enum, auto
from typing import Any, Callable, List, NamedTuple

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

NormalModeHandlerType = Callable[[QPlainTextEdit], Any]


class Modes(str, Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    VISUAL = "VISUAL"
    VISUAL_LINE = "VISUAL_LINE"
    COMMAND = "COMMAND"
    MARKS = "MARKS"


class EventParams(NamedTuple):
    cursor: QTextCursor
    keys: str
    modifiers: List[str]
    event: QKeyEvent
    visual: bool
    mode: Modes     
