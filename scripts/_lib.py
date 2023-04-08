import json
from pymongo import MongoClient
from pymongo.database import Database


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def get_db() -> Database:
    config = load_json("data/db/config.json")
    host, port, db_name = config["host_name"], config["port"], config["db_name"]
    return MongoClient(f"mongodb://{host}:{port}/")[db_name]
