from enum import Enum
from typing import Any, List, Callable, NamedTuple

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

HandlerType = Callable[[QPlainTextEdit], Any]


class Modes(str, Enum):
    NORMAL = 'NORMAL'
    INSERT = 'INSERT'
    VISUAL = 'VISUAL'
    VISUAL_LINE = 'VISUAL_LINE'
    COMMAND = 'COMMAND'
    MARKS = 'MARKS'
    SEARCH = 'SEARCH'


class EventParams(NamedTuple):
    cursor: QTextCursor
    keys: str
    modifiers: List[str]
    event: QKeyEvent
    visual: bool
    mode: Modes
