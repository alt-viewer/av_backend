from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio
from statistics import mean
import toolz.curried as toolz

query = gql(
    """
    query char_items {
        queryCharacter {
            items {
                xid
            }
        }
    }
    """
)


async def main():
    async with Client(transport=AIOHTTPTransport("http://localhost:8080/graphql")) as c:
        res = await c.execute(query)
        chars = res["queryCharacter"]
        count_items = toolz.compose(len, toolz.get_in(["items"]))
        mean_items = mean(map(count_items, chars))
        print(
            f"The average number of items for {len(chars)} characters was {mean_items}"
        )
        return chars


if __name__ == "__main__":
    asyncio.run(main())
