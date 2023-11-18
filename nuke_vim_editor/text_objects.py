
from enum import Enum
from typing import Tuple, Union, Optional

from .profiling import profile


class MatchingBrackets(str, Enum):
    PARENTHESIS = '()'
    SQUARE_BRACKETS = '[]'
    BRACKETS = '{}'


def find_matching(text: str, pos: int, m: MatchingBrackets) -> Optional[tuple[int, int]]:

    unbalanced = False
    closing_bracket = None
    opening_backet = None

    if text[pos:][0] == m[0]:
        pos += 1

    # Forward search for the closing bracket
    for i, char in enumerate(text[pos:]):

        if char == m[0]:  # open bracket
            unbalanced = True

        elif char == m[1]:  # close bracket
            if not unbalanced:
                closing_bracket = i + pos
                break
            unbalanced = False

    if closing_bracket is None or unbalanced:
        return None

    # Backward search for the opening bracket
    left = text[:pos]
    for i in range(pos - 1, -1, -1):
        char = left[i]

        if char == m[1]:  # close bracket
            unbalanced = True

        elif char == m[0]:  # open bracket
            if not unbalanced:
                opening_backet = i
                break
            unbalanced = False

    if opening_backet is None or unbalanced:
        return None

    return (opening_backet, closing_bracket)


def find_matching_parenthesis(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.PARENTHESIS)


def find_matching_square_brackets(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.SQUARE_BRACKETS)


def find_matching_brackets(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.BRACKETS)
