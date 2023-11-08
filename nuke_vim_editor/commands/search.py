from bisect import bisect_left
from typing import List, Optional

from PySide2.QtWidgets import QPlainTextEdit

Positions = List[int]


def _find_next_down(positions: Positions, position: int):
    idx = bisect_left(positions, position)

    if idx >= len(positions):
        return positions[0]

    if positions[idx] == position:
        idx += 1

    return positions[0] if idx == len(positions) else positions[idx]


def _find_next_up(positions: Positions, position: int):
    idx = bisect_left(positions, position)
    return positions[-1] if idx == 0 else positions[idx - 1]


def _find(search: str, text: str):
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


class SearchCommand:
    history: Positions = []
    last_search: Optional[str] = None

    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor

    def find(self, search: str):
        """Populate the history with the search results."""
        self.last_search = search
        self.history = _find(search, self.editor.toPlainText())

    def find_next_down(self, position: int):
        if not self.last_search or not self.history:
            return None

        self.find(self.last_search)
        return _find_next_down(self.history, position)

    def find_next_up(self, position: int):
        if not self.last_search or not self.history:
            return None

        self.find(self.last_search)
        return _find_next_up(self.history, position)
