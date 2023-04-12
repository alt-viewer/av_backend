from collections.abc import Awaitable, Callable, Iterable
from functools import partial, wraps
from logging import getLogger
from typing import Any, Generic, TypeAlias, TypedDict, TypeVar

import toolz.curried as toolz
from aiohttp import ClientSession
from dotenv import dotenv_values
from yarl import URL

from entities.converters import JSON, Converter, with_conversion

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


class Filter(TypedDict):
    pass


FilterType = TypeVar("FilterType", bound=Filter)
Params: TypeAlias = dict[str, str]
Fields: TypeAlias = list[str]
Joins: TypeAlias = list[str]

ParamFactory: TypeAlias = Callable[
    [FilterType | None, Fields | None, Joins | None], Params
]
T = TypeVar("T")


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


def convert_filter_value(value: object) -> str:
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
    """
    Create a factory for Census API query params.
    `fields`: the fields to project. Corresponds to c:show.
    `joins`: the collections to join. Corresponds to c:resolve.
    See also: http://census.daybreakgames.com/#query-commands
    """

    @toolz.curry
    def factory(
        filters: FilterType | None = None,
        fields: Fields | None = None,
        joins: Joins | None = None,
    ) -> Params:
        return {
            "c:lang": "en",
            "c:show": commas(fields if fields is not None else default_fields),
            "c:resolve": commas(joins if joins is not None else default_joins),
        } | {key: convert_filter_value(value) for key, value in (filters or {}).items()}

    return factory


def result_of(path: str, json: JSON) -> list[JSON]:
    """Get the results from a Census response based on its path"""
    xs = json[f"{path}_list"]
    if not isinstance(xs, list):
        raise RuntimeError("Could not identify result list")
    return xs


# I couldn't find a way to have two signatures for `census_query`:
#   - `Filter` type provided: require `Filter` with filled values in the output function
#   - No filter: omit the filter argument in the output function
# My solution was to split it into two functions and make the `filters` argument optional in `query`.
# I've made two public wrappers: one with a `Filter` and one without
def _census_query(
    path: str,
    make_params: ParamFactory,
    convert: Converter,
) -> Callable[
    [ClientSession, FilterType | None, Fields | None, Joins | None],
    Awaitable[list[T]],
]:
    @with_conversion(convert)
    async def query(
        session: ClientSession,
        filters: FilterType | None = None,
        fields: Fields | None = None,
        joins: Joins | None = None,
    ) -> list[JSON]:
        params = make_params(filters, fields, joins)
        url = census_url(path, params)
        async with session.get(url) as response:
            if not response.ok:
                raise RuntimeError(
                    f'Request for {response.url} failed with status {response.status} because "{response.reason}"'
                )
            json = await response.json()
        return result_of(path, json)

    return query


# I made this a callable class because `Callable` can't have optional arguments.
# I decided to name them with snake_case to make it look like a function to a user
class census_query:
    """
    Create a query for a collection. Does not allow filtering such as `item_id=4`.
    Use `filtered_census_query` for that.
    """

    def __init__(
        self,
        path: str,
        make_params: ParamFactory,
        convert: Converter,
    ):
        self.path = path
        self.make_params = make_params
        self.convert = convert

    async def __call__(
        self,
        session: ClientSession,
        fields: Fields | None = None,
        joins: Joins | None = None,
    ) -> list[T]:
        return await _census_query(self.path, self.make_params, self.convert)(
            session, None, fields, joins
        )


class filtered_census_query(Generic[FilterType]):
    """See `census_query`"""

    def __init__(self, path: str, make_params: ParamFactory, convert: Converter):
        self.path = path
        self.make_params = make_params
        self.convert = convert

    async def __call__(
        self,
        session: ClientSession,
        filters: FilterType,
        fields: Fields | None = None,
        joins: Joins | None = None,
    ) -> list[T]:
        return await _census_query(self.path, self.make_params, self.convert)(
            session, filters, fields, joins
        )


def finalise_query(query):
    """Prevent overriding the fields and joins of a query"""
    return partial(query, fields=None, joins=None)
