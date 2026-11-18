from enum import Enum


class Modes(str, Enum):
    NORMAL = 'NORMAL'
    INSERT = 'INSERT'
    VISUAL = 'VISUAL'
    VISUAL_LINE = 'VISUAL_LINE'
    YANK = 'YANK'
    DELETE = 'DELETE'
    CHANGE = 'CHANGE'


class _EditorMode:
    mode: Modes = Modes.NORMAL


EditorMode = _EditorMode()
