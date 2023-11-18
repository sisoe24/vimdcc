from enum import Enum
from typing import List, Optional


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
    quote_type: str,
    start_pos: int,
    end_pos: int
) -> Optional[tuple[int, int]]:

    # Adjust start position if it's on a quote
    if text[start_pos:][0] == quote_type:
        start_pos += 1

    end_index = None

    # Forward search for the closing quote
    i = start_pos
    while i < end_pos:
        if text[i] == '\\' and i + 1 < end_pos and text[i + 1] == quote_type:
            i += 2  # Skip escaped quote
            continue

        if text[i] == quote_type:
            end_index = i
            break

        i += 1

    if end_index is None:
        return None

    start_index = None

    # Backward search for the opening quote
    i = start_pos - 1
    while i >= 0:
        if i > 0 and text[i - 1] == '\\' and text[i] == quote_type:
            i -= 2  # Skip escaped quote
            continue

        if text[i] == quote_type:
            start_index = i
            break

        i -= 1

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
