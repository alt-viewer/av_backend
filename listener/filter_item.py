"""
Filter item payloads to only those that are account wide.
This model is required because the developers removed the `account_level`
flag from the `characters_item` collection.
"""

from json import load
import toolz.curried as toolz

from entities.payloads import ItemAdded

# Load whitelist
with open("data/account_wide.json") as f:
    json = load(f)
    whitelist = set(map(int, json["item_list"]))


def is_account_wide(item: ItemAdded) -> bool:
    return item.item_id in whitelist
