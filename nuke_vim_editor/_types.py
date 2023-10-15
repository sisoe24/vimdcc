from typing import Any, List, Callable, NamedTuple

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from .editor_state import Modes

HandlerType = Callable[[QPlainTextEdit], Any]


class EventParams(NamedTuple):
    cursor: QTextCursor
    keys: str
    modifiers: List[str]
    event: QKeyEvent
    visual: bool
    mode: Modes
