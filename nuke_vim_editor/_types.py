from typing import Any, List, Callable
from dataclasses import field, dataclass

from PySide2.QtGui import QKeyEvent, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit

from .status_bar import _StatusBar, status_bar
from .editor_state import Modes

HandlerType = Callable[[QPlainTextEdit], Any]


@dataclass
class EventParams:
    cursor: QTextCursor
    event: QKeyEvent

    keys: str
    modifiers: List[str]

    mode: Modes

    visual: bool = field(init=False)
    anchor: QTextCursor.MoveMode = field(init=False)
    status_bar: _StatusBar = field(init=False)

    def __post_init__(self):
        self.visual = self.mode in [Modes.VISUAL, Modes.VISUAL_LINE, Modes.YANK]
        self.anchor = QTextCursor.KeepAnchor if self.visual else QTextCursor.MoveAnchor
        self.status_bar = status_bar
