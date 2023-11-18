from typing import Tuple
from dataclasses import dataclass

import pytest

from nuke_vim_editor.text_objects import (MatchingBrackets,
                                          find_matching_brackets,
                                          find_matching_parenthesis,
                                          find_matching_square_brackets)

# I am lazy I know :D
P = MatchingBrackets.PARENTHESIS
S = MatchingBrackets.SQUARE_BRACKETS
B = MatchingBrackets.BRACKETS


@dataclass
class MatchTest:
    string: str
    pattern: MatchingBrackets
    start: int
    expected: Tuple[int, int]


@pytest.mark.parametrize('data', [
    MatchTest('()', P, 0, (0, 1)),
    MatchTest('(abcde)', P, 1, (0, 6)),
    MatchTest('(1, 2, (3, 4), 5)', P, 7, (7, 12)),
    MatchTest('(1, 2, (3, 4), 5)', P, 8, (7, 12)),
    MatchTest('(1, 2, (3, 4), 5)', P, 9, (7, 12)),
    MatchTest('(1, 2, (3, 4), 5)', P, 12, (7, 12)),
    MatchTest('(1, 2, (3, 4), 5)', P, 13, (0, 16)),
    MatchTest('(1, \n2, (3,\n\t4), 5)', P, 9, (8, 14)),
    MatchTest('(1, (), 3)', P, 4, (4, 5)),
    MatchTest('x(text(), cursor.position(), "()")', P, 2, (1, 33)),
])
def test_find_brackets(data: MatchTest):
    find = find_matching_parenthesis(data.string, data.start)
    assert find == data.expected
