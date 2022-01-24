from pydgraph import DgraphClient
from typing import Iterator

from entities import DBCharacter

def query(client: DgraphClient) -> dict:
    return txn.query("""
                     query all_chars {
                         all_chars(func: (has: faction_id)) {
                            name
                            id
                            outfit_tag
                            outfit_id
                            faction_id
                            server_id:
                            battle_rank
                            last_login
                            items
                            peers
                            eliminated
                         }
                     }
                     """)

def all_chars(client: DgraphClient) -> Iterator[DBCharacter]:
    