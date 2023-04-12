from yarl import URL
from logging import getLogger
from dotenv import dotenv_values
from typing import TypeAlias, Any, TypedDict, TypeVar
from collections.abc import Callable, Iterable, Awaitable
from functools import wraps, partial
import toolz.curried as toolz
from aiohttp import ClientSession, ClientResponse

from entities import XID
from entities.converters import Converter, with_conversion, JSON, JSONValue

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
Fields: TypeAlias = list[str]
Joins: TypeAlias = list[str]
FilterValue: TypeAlias = str | int | list
Filter = TypedDict("Filter", {"field_name": str, "field_value": FilterValue})
ParamFactory: TypeAlias = Callable[[Fields, Joins, list[Filter]], Params]
T = TypeVar("T")

query_logger = getLogger("census query")


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


def convert_filter_value(value: FilterValue) -> str:
    converters = {
        str: toolz.identity,
        int: str,
        list: toolz.map(str),
    }
    t = type(value)
    if t not in converters:
        raise ValueError(f"Unhandled `FilterValue` type. Add a converter for {t}")
    return converters[t](value)


def param_factory(default_fields: Fields, default_joins: Joins) -> ParamFactory:
    @toolz.curry
    def factory(fields: Fields, joins: Joins, filters: list[Filter]) -> Params:
        return {
            "c:lang": "en",
            "c:show": commas(fields or default_fields),
            "c:resolve": commas(joins or default_joins),
        } | {f["field_name"]: convert_filter_value(f["field_value"]) for f in filters}

    return factory


def result_of(path: str, json: JSON) -> list[JSON]:
    """Get the results from a Census response based on its path"""
    xs = json[f"{path}_list"]
    if not isinstance(xs, list):
        raise RuntimeError("Could not identify result list")
    return xs


def default_fail(r: ClientResponse) -> None:
    query_logger.error(
        f'Request for {r.url} failed with status {r.status} because "{r.reason}"'
    )


async def census_query(
    path: str,
    make_params: ParamFactory,
    convert: Converter,
    on_fail: Callable[[ClientResponse], None] | None = None,
) -> Callable[[ClientSession, list[Filter]], Awaitable[T | None]]:
    @toolz.curry
    @with_conversion(convert)
    async def query(
        session: ClientSession, fields: Fields, joins: Joins, filters: list[Filter]
    ) -> list[JSON] | None:
        params = make_params(fields, joins, filters)
        url = census_url(path, params)
        async with session.get(url) as response:
            if not response.ok:
                return (on_fail or default_fail)(response)
            json = await response.json()
        return result_of(path, json)

    return query
