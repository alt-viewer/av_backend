from pydgraph import DgraphClient
from toolz import curry
from typing import Iterator, Callable


@curry
def batch_mutate(
    client: DgraphClient, error_handler: Callable[[Exception], None], xs: Iterator[dict]
) -> None:
    txn = client.txn()
    try:
        for x in xs:
            txn.mutate(set_obj=x)
        txn.commit()
    except Exception as e:
        error_handler(e)
    finally:
        txn.discard()
