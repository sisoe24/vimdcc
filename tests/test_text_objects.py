from typing import Tuple, Optional
from dataclasses import dataclass

import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QPlainTextEdit

from nuke_vim_editor.text_objects import (MatchingCharacter,
                                          find_matching_quotes,
                                          find_matching_brackets)

PB = MatchingCharacter.PARENTHESIS
SB = MatchingCharacter.SQUARE_BRACKETS
BB = MatchingCharacter.BRACKETS


@dataclass
class MatchTest:
    text: str
    char: MatchingCharacter
    find: Optional[Tuple[int, int]]
    start: int
    end: int = -1

    def __post_init__(self):
        if self.end == -1:
            self.end = len(self.text)


@pytest.mark.parametrize(
    'data',
    [
        MatchTest('()', PB, (0, 1), 0),
        MatchTest('(abcde)', PB, (0, 6), 1),
        MatchTest('(1, 2, (3, 4), 5)', PB, (7, 12), 7),
        MatchTest('(1, 2, (3, 4), 5)', PB, (7, 12), 8),
        MatchTest('(1, 2, (3, 4), 5)', PB, (7, 12), 9),
        MatchTest('(1, 2, (3, 4), 5)', PB, (7, 12), 12),
        MatchTest('(1, 2, (3, 4), 5)', PB, (0, 16), 13),
        MatchTest('(1, \n2, (3,\n\t4), 5)', PB, (8, 14), 9),
        MatchTest('(1, (), 3)', PB, (4, 5), 4),
        MatchTest('x(text(), cursor.position(), "()")', PB, (1, 33), 2),
        MatchTest('some text', PB, None, 0),
        MatchTest('some text', PB, None, 3),
        MatchTest('(1, 2, (3, 4, (5), )', PB, None, 2),
    ]
)
def test_find_brackets(data: MatchTest):
    find = find_matching_brackets(data.text, data.char, data.start, -1)
    assert find == data.find


DQ = MatchingCharacter.DOUBLE_QUOTES
SQ = MatchingCharacter.SINGLE_QUOTES
BQ = MatchingCharacter.BACKTICK


@pytest.fixture()
def editor(qtbot: QtBot):
    return QPlainTextEdit()


@pytest.mark.parametrize(
    'data',
    [
        MatchTest('"foo"', DQ, (0, 4), 0),
        MatchTest("'foo'", SQ, (0, 4), 1),
        MatchTest('`foo`', BQ, (0, 4), 2),
        MatchTest('"foo \\"bar\\" "', DQ, (0, 13), 1),
        MatchTest("'foo \\'bar\\' '", SQ, (0, 13), 1),
        MatchTest('`foo \\`bar\\` `', BQ, (0, 13), 1),
        MatchTest('"foo bar', DQ, None, 1),
        MatchTest("'foo bar", SQ, None, 1),
        MatchTest('`foo bar', BQ, None, 1),
        MatchTest('"foo \\"b\\" \\"a\\" r\\" "', DQ, (0, 21), 1),
        MatchTest('"foo \\"bar\\" "', DQ, (0, 13), 8),
    ]
)
def test_find_quotes(data: MatchTest, editor: QPlainTextEdit):
    editor.insertPlainText(data.text)
    find = find_matching_quotes(editor.toPlainText(), data.char, data.start, data.end)
    assert find == data.find
