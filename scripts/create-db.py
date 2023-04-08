from pymongo import MongoClient
from json import load

from _lib import get_db, load_json


print("Loading data...")
char_validator = load_json("data/db/validators/characters.json")

# Create DB
print("Creating database...")
db = get_db()
print("Database created successfully")

# Create collections
print("Creating collections...")
db.create_collection("characters", validator=char_validator)
print("Created collections successfully")
