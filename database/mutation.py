from pydgraph import Txn, Request
import toolz.curried as toolz
from operator import methodcaller
from typing import Iterator


@toolz.curry
def mutations(txn: Txn, xs: Iterator) -> Request:
    """
    Create a request for multiple mutations.
    Each member of xs must have a .json() method.
    """
    return toolz.pipe(
        xs,
        toolz.map(methodcaller("json")),
        toolz.map(lambda j: txn.create_mutation(set_obj=j)),
        lambda ms: txn.create_request(mutations=ms),
    )
