from entities import MatchChar, Item
from toolz.curried import get_in


def convert_item(i: dict) -> Item:
    return Item(i["xid"], i["last_recorded"])


def convert_matchchar(char: dict) -> MatchChar:
    return MatchChar(
        uid=char["id"],
        last_login=char["last_login"],
        items=list(map(convert_item, char["items"])),
        eliminated=list(map(get_in(["id"]), char["eliminated"])),
    )
