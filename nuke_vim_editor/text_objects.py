
from enum import Enum
from typing import Tuple, Union, Optional

from .profiling import profile


class MatchingBrackets(str, Enum):
    PARENTHESIS = '()'
    SQUARE_BRACKETS = '[]'
    BRACKETS = '{}'


def find_matching(text: str, pos: int, m: MatchingBrackets):

    unbalanced = False
    closing_bracket = None
    opening_backet = None

    for i, char in enumerate(text[pos:]):

        if char == m[0]:  # open bracket
            unbalanced = True

        elif char == m[1]:  # close bracket
            if not unbalanced:
                closing_bracket = i + pos
                break
            unbalanced = False

    if not closing_bracket or unbalanced:
        return None

    for i in range(closing_bracket - 1, -1, -1):
        char = text[i]

        if char == m[1]:  # close bracket
            unbalanced = True

        elif char == m[0]:  # open bracket
            if not unbalanced:
                opening_backet = i + 1
                break
            unbalanced = False

    if not opening_backet or unbalanced:
        return None

    return (opening_backet, closing_bracket)


def find_matching_parenthesis(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.PARENTHESIS)


def find_matching_square_brackets(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.SQUARE_BRACKETS)


def find_matching_brackets(text: str, pos: int):
    return find_matching(text, pos, MatchingBrackets.BRACKETS)
