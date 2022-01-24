from operator import methodcaller

from entities import Character

char_to_json = methodcaller("json")


def char_jsons(chars: list[Character]) -> list[dict]:
    return list(map(char_to_json, chars))
