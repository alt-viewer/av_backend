from database import GQLClient, gql
from entities import NodeTypes
from toolz.curried import get_in


def make_query_name(field: NodeTypes) -> str:
    """Convert the node enum to a query name."""
    return "aggregate" + field.value


def create_query(query_name: str):
    """Dynamically create the query based on the field."""
    return gql(
        # This ugliness is because format strings
        # can't contain curlies
        "query count_chars {"
        + query_name
        + """
                {
                count
            }
        }
        """
    )


async def count(session: GQLClient, field: NodeTypes) -> int:
    """Count how many nodes of a given type exist."""
    query_name = make_query_name(field)
    return (await session.execute(create_query(query_name)))[query_name]["count"]
