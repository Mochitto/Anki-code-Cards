import logging
import re
from typing import Dict, List, Tuple

import card_types as Types
from card_error import CardError
from debug_tools import expressive_debug

logger = logging.getLogger(__name__)


def get_clozes(text: Types.MDString) -> List[Types.ClozeType]:
    """
    Extract clozes from text.

    Pattern:
    {{c1::something}}
    {{C9::something}}
    """
    clozes_regex = re.compile(r"(?i){{c(\d)::(.+?)}}")

    clozes_matches = clozes_regex.findall(text)

    return clozes_matches


def hash_clozes(clozes: List[Tuple[str, str]]) -> Dict[str, Tuple[str, str]]:
    """
    Transform matches from re.findall into a dictionary that has:
    keys: hashed match
    values: (cloze's number, match)
    """

    # A dictionary built to use with translate()
    # key: ord(number), value: letter + "-" : Z
    number_to_letter_translation = {
        48: "A",
        49: "B",
        50: "C",
        51: "D",
        52: "E",
        53: "F",
        54: "G",
        55: "H",
        56: "I",
        57: "J",
        45: "Z",
    }

    result = dict()
    for cloze_number, cloze_text in clozes:
        hash_number = str(hash(cloze_text))

        hash_in_letters = hash_number.translate(number_to_letter_translation)
        result[hash_in_letters] = (cloze_number, cloze_text)

    return result


def replace_cloze_text_with_hashes(
    markdown_code: Types.MDString, hashed_clozes: Dict[str, Tuple[str, str]]
) -> Types.MDString:
    """
    Replace the text of clozes ({{c1::This part}}) with the corresponding hash.

    Raise an error if there are no matches, the reasons could be:
    - The cloze is not a full word/number
    - There are other clozes that are sub-strings of the one that you are matching
    - Your cloze is a sub-string of another cloze, so it was already taken
    """
    if not hashed_clozes:
        return markdown_code

    code_with_hashes = markdown_code
    for hash_key, cloze_match in hashed_clozes.items():
        cloze_regex = re.compile(rf"\b{cloze_match[1]}\b")
        code_with_hashes, number_of_substitutions = re.subn(cloze_regex, hash_key, code_with_hashes)
        if not number_of_substitutions:
            raise CardError(
                "Bad formatting in code's cloze; clozes should:\n"
                + "- Be full words/numbers\n"
                + "- Not be a sub-string of another cloze\n"
                + "- Not have sub-strings of another cloze\n"
            )

    return code_with_hashes


def clean_code_from_clozes(text: Types.MDString) -> Types.MDString:
    """
    Replace clozes with their just their text, in the given text.
    """
    clozes_regex = re.compile(r"{{c(\d)::(.+?)}}")

    text_without_clozes = re.sub(clozes_regex, r"\2", text)

    return text_without_clozes


def inject_clozes(text: Types.HTMLString, hashed_clozes: Dict[str, Tuple[str, str]]) -> Types.HTMLString:
    """
    Replace the hashes in the text with the corresponding cloze:
    HSJDKASKHDAKS -> {{c1::my cloze}}
    """
    new_text = text

    for hashed_cloze, cloze_match in hashed_clozes.items():
        number = cloze_match[0]
        clozed_text = cloze_match[1]

        word_regex = re.compile(rf"\b{hashed_cloze}\b")

        new_text = re.sub(word_regex, f"{{{{c{number}::{clozed_text}}}}}", new_text)

    return new_text


def are_clozes_in_card(card: Dict[str, Types.HTMLString]) -> bool:
    """
    Check if in the front of the card there is at least one cloze

    Dict:
    "front": HTMLString
    "back": HTMLString

    Pattern:
    {{c1::something}}
    {{C5::something else}}
    """
    clozes_regex = re.compile(r"{{c(\d)::(.+?)}}")
    front = card["front"]

    return bool(clozes_regex.search(front))
