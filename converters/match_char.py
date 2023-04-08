from toolz.curried import get_in

from entities import MatchChar, Item
from converters.item import items_from_db


def convert_matchchar(char: dict) -> MatchChar:
    """
    Convert a database response for a character to
    a format specialised for character matching
    """
    return MatchChar(
        uid=char["id"],
        last_login=char["last_login"],
        items=items_from_db(char["items"]),
        eliminated=list(map(get_in(["id"]), char["eliminated"])),
    )
