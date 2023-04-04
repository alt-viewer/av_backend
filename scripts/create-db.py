from pymongo import MongoClient
from json import load


def load_json(path: str) -> dict:
    with open(path) as f:
        return load(f)


print("Loading data...")
config = load_json("data/db/config.json")
char_validator = load_json("data/db/validators/characters.json")

# Create DB
print("Creating database...")
host, port = config["host_name"], config["port"]
client: MongoClient = MongoClient(f"mongodb://{host}:{port}/")
db = client["altViewerDB"]
print("Database created successfully")

# Create collections
print("Creating collections...")
db.create_collection("characters", validator=char_validator)
print("Created collections successfully")