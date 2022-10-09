from yarl import URL
from logging import getLogger
from dotenv import dotenv_values

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


def query(path: str | None = None, params: dict = None, websocket: bool = False) -> URL:
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
