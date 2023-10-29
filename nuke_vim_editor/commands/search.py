from bisect import bisect_left
from typing import Any, List

from PySide2.QtWidgets import QPlainTextEdit

from ..base_command import Command

Positions = List[int]


def _find_next_down(positions: Positions, position: int):
    # If the target is greater than the last element in the list
    idx = bisect_left(positions, position)

    # if index is greater than the length of the list, return the first
    if idx >= len(positions):
        return positions[0]

    # If the target is equal, go to the next element
    if positions[idx] == position:
        idx += 1

    return positions[0] if idx == len(positions) else positions[idx]


def _find_next_up(positions: Positions, position: int):

    idx = bisect_left(positions, position)

    # If the target is smaller than the first element in the list
    return positions[-1] if idx == 0 else positions[idx - 1]


def _find(search: str, text: str):
    search = search.strip()

    positions: Positions = []
    word_len = len(search)

    if word_len == 1:
        return [i for i, letter in enumerate(text) if letter == search]

    next_letter = ''

    for char, letter in enumerate(text, 1):
        next_letter = next_letter[-(word_len - 1):] + letter
        if next_letter == search:
            positions.append(char - word_len)

    return positions


class SearchCommand(Command):
    search_history: Positions = []
    editor: QPlainTextEdit = None
    last_search: str = ''

    def __new__(cls, editor: QPlainTextEdit, *args: Any, **kwargs: Any):
        cls.editor = editor
        if not hasattr(cls, '_instance'):
            cls._instance = super(SearchCommand, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def find(cls, search: str):
        cls.last_search = search
        if not cls.editor:
            raise RuntimeError('Editor not set')
        cls.search_history = _find(search, cls.editor.toPlainText())

    @classmethod
    def find_next_down(cls, position: int):
        cls.find(cls.last_search)
        return (
            _find_next_down(cls.search_history, position)
            if cls.search_history
            else None
        )

    @classmethod
    def find_next_up(cls, position: int):
        cls.find(cls.last_search)
        return (
            _find_next_up(cls.search_history, position)
            if cls.search_history
            else None
        )
