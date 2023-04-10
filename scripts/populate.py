from pymongo import MongoClient
from datetime import datetime

from _lib import load_json, get_db


def replace_date(d: dict) -> dict:
    DATE_FIELDS = {"lastLogin", "lastRecorded"}
    for key, value in d.items():
        if key in DATE_FIELDS:
            d[key] = datetime.now()
        elif isinstance(value, list):
            d[key] = [replace_date(x) for x in value]
        elif isinstance(value, dict):
            d = replace_date(d)
    return d


def add_dates(chars: list[dict]) -> list[dict]:
    return list(map(replace_date, chars))


chars = load_json("data/db/population.json")["characters"]
chars_with_dates = add_dates(chars)
db = get_db()
db.characters.insert_many(chars_with_dates)
