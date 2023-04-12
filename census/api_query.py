from yarl import URL
from logging import getLogger
from dotenv import dotenv_values
from typing import TypeAlias, Any
from collections.abc import Callable, Iterable
from functools import wraps
import toolz.curried as toolz

from entities import XID
from entities.converters import Converter

env_id = dotenv_values(".env").get("SERVICE_ID")
if env_id is None:
    raise EnvironmentError("No service ID in the .env file")

if not env_id.startswith("s:"):
    getLogger("Service ID").warn("Incorrect service ID format. Should start with 's:'")
    service_id = "s:" + env_id
else:
    service_id = env_id


def http_path(path: str | None, service_id: str) -> str:
    return f"/{service_id}/get/ps2:v2/" + (path or "")


Params: TypeAlias = dict[str, str]


def _census_url(
    service_id: str,
    path: str | None = None,
    params: Params | None = None,
    websocket: bool = False,
) -> URL:
    """Construct a PS2 API query."""
    query = params or {}
    query.update({"service-id": service_id} if websocket else {})
    full_path = "/streaming" if websocket else http_path(path, service_id)
    return URL.build(
        scheme="wss" if websocket else "https",
        host="push.planetside2.com" if websocket else "census.daybreakgames.com",
        path=full_path,
        query=query,
    )


census_url = partial(_census_url, service_id)


def commas(xs: Iterable[Any]) -> str:
    return ",".join(xs)


Fields: TypeAlias = list[str]
Joins: TypeAlias = list[str]
ParamFactory: TypeAlias = Callable[[Fields, Joins], Params]


def param_factory(default_fields: Fields, default_joins: Joins) -> ParamFactory:
    return lambda fields, joins: {
        "c:show": commas(fields or default_fields),
        "c:resolve": commas(joins or default_joins),
        "c:lang": "en",
    }


def with_ids(
    factory: ParamFactory,
) -> Callable[[str, Fields, Joins, list[XID]], Params]:
    @wraps(factory)
    @toolz.curry
    def wrapper(
        field_name: str, fields: Fields, joins: Joins, ids: list[XID]
    ) -> Params:
        return {**factory(fields, joins), field_name: commas(map(str, ids))}

    return wrapper


# TODO: A factory for census request functions.
# ParamFactory -> Converter -> (ClientSession -> Optional[Fields] -> Optional[Joins] -> list[T])
async def collection_query(make_params: ParamFactory, convert: Converter):
    def make_query(path: str, fields: Fields, joins: Joins) -> URL:
        return census_url(
            path=path,
            params=make_params(fields, joins),
        )

    async def do_query():
        pass

    return make_query


# TODO: a wrapper around `collection_query` that wraps the factory using `with_ids`
# allowing filtered requests.
# ParamFactory -> Converter -> (ClientSession -> String -> Optional[Fields] -> Optional[Joins] -> [XID] -> list[T])
