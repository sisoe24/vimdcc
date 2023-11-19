from typing import List
from dataclasses import field, dataclass

from PySide2.QtGui import QKeyEvent, QTextCursor

from .status_bar import StatusBar, status_bar
from .editor_mode import Modes


@dataclass
class HandlerParams:
    cursor: QTextCursor
    event: QKeyEvent

    keys: str
    modifiers: List[str]

    mode: Modes

    visual: bool = field(init=False)
    anchor: QTextCursor.MoveMode = field(init=False)
    status_bar: StatusBar = field(init=False)

    def __post_init__(self):
        self.visual = self.mode in [Modes.VISUAL, Modes.VISUAL_LINE, Modes.YANK,
                                    Modes.DELETE, Modes.CHANGE]
        self.anchor = QTextCursor.KeepAnchor if self.visual else QTextCursor.MoveAnchor
        self.status_bar = status_bar
