from enum import Enum, auto


class Modes(Enum):
    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()


class EditorMode:
    mode = Modes.NORMAL
