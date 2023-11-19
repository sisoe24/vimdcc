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
    _mode: Modes = Modes.NORMAL

    def __new__(cls):
        if hasattr(cls, '_instance') is False:
            cls._instance = super(_EditorMode, cls).__new__(cls)
        return cls._instance

    @property
    def mode(self) -> Modes:
        return self._mode

    @mode.setter
    def mode(self, mode: Modes):
        self._mode = mode


EditorMode = _EditorMode()
