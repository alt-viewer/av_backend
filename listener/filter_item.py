"""
Filter item payloads to only those that are account wide.
This model is required because the developers removed the `account_level`
flag from the `characters_item` collection.
"""

from json import load
import toolz.curried as toolz

from payloads import ItemAdded

# Load whitelist
with open("static_data/account_wide.json") as f:
    json = load(f)
    categories = set(json["category_ids"])
    whitelist = set(json["item_ids"])

def is_account_wide(item: ItemAdded) -> bool:
    ...