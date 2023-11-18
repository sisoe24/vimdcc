from enum import Enum
from typing import List, Optional

from .profiling import profile


class MatchingCharacter(str, Enum):
    PARENTHESIS = '()'
    SQUARE_BRACKETS = '[]'
    BRACKETS = '{}'

    DOUBLE_QUOTES = '"'
    SINGLE_QUOTES = "'"
    BACKTICK = '`'


def find_matching_brackets(
    text: str,
    bracket_type: MatchingCharacter,
    start_pos: int,
    end_pos: int
) -> Optional[tuple[int, int]]:

    if end_pos == -1:
        end_pos = len(text)

    open_brackets: List[int] = []
    closing_bracket = None
    opening_bracket = None

    # Adjust start position if it's on an open bracket
    if text[start_pos:][0] == bracket_type[0]:
        start_pos += 1

    # Forward search for the closing bracket
    for i, char in enumerate(text[start_pos:end_pos], start_pos):
        if char == bracket_type[0]:  # Open bracket
            open_brackets.append(i)

        elif char == bracket_type[1]:  # Close bracket
            if not open_brackets:
                closing_bracket = i
                break
            open_brackets.pop()

    if closing_bracket is None or open_brackets:
        return None

    # Backward search for the opening bracket
    left = text[:start_pos]
    open_brackets = []
    for i in range(start_pos - 1, -1, -1):
        char = left[i]

        if char == bracket_type[1]:  # Close bracket
            open_brackets.append(i)

        elif char == bracket_type[0]:  # Open bracket
            if not open_brackets:
                opening_bracket = i
                break
            open_brackets.pop()

    if opening_bracket is None or open_brackets:
        return None

    return (opening_bracket, closing_bracket)


def find_matching_quotes(
    text: str,
    quote_type: MatchingCharacter,
    start_pos: int,
    end_pos: int
) -> Optional[tuple[int, int]]:

    if text[start_pos:][0] == quote_type:
        start_pos += 1

    escaped = False
    end_index = None

    for i, char in enumerate(text[start_pos:end_pos], start_pos):

        if char == '\\' and text[i + 1] == quote_type:
            escaped = True
            continue

        if char == quote_type and escaped:
            escaped = False
            continue

        if char == quote_type:
            end_index = i
            break

    if end_index is None:
        return None

    start_index = None
    for i in range(start_pos - 1, -1, -1):
        char = text[i]

        if char == quote_type:
            if text[i - 1] == '\\':
                escaped = True

            if escaped:
                escaped = False
                continue

            start_index = i
            break

    if start_index is None:
        return None

    return start_index, end_index


def find_matching(
    text: str,
    character: MatchingCharacter,
    start_pos: int,
    end_pos: int = -1
) -> Optional[tuple[int, int]]:
    """Find the matching character for the given character at the given position.

    Args:
        text (str): The text to search in.
        character (MatchingCharacter): The character to find the matching character for.
        start_pos (int): The position to start searching from.
        end_pos (int, optional): The position to stop searching at. Defaults to -1.

    Returns:
        Optional[tuple[int, int]]: The start and end positions of the matching character.
    """
    if character in [MatchingCharacter.PARENTHESIS, MatchingCharacter.SQUARE_BRACKETS,
                     MatchingCharacter.BRACKETS]:
        return find_matching_brackets(text, character, start_pos, end_pos)

    if character in [MatchingCharacter.SINGLE_QUOTES, MatchingCharacter.DOUBLE_QUOTES,
                     MatchingCharacter.BACKTICK]:
        return find_matching_quotes(text, character, start_pos, end_pos)

    return None
