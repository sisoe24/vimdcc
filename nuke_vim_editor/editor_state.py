from enum import Enum


class Modes(str, Enum):
    NORMAL = 'NORMAL'
    INSERT = 'INSERT'
    VISUAL = 'VISUAL'
    VISUAL_LINE = 'VISUAL_LINE'
    COMMAND = 'COMMAND'
    MARKS = 'MARKS'
    SEARCH = 'SEARCH'
    YANK = 'YANK'


class _EditorState:
    _mode: Modes = Modes.NORMAL

    def __new__(cls):
        if hasattr(cls, '_instance') is False:
            cls._instance = super(_EditorState, cls).__new__(cls)
        return cls._instance

    @property
    def mode(self) -> Modes:
        return self._mode

    @mode.setter
    def mode(self, mode: Modes):
        self._mode = mode


EditorState = _EditorState()
