from yarl import URL
from pkgutil import get_data

# Getting the service ID in a way that should be indifferent
# to the current working directory
file_content = get_data("av_backend", "service_id.txt")
if not file_content:
    raise RuntimeError("Unable to load service ID")
service_id = file_content.decode("utf-8")


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
