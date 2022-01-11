from yarl import URL

with open("service_id.txt") as f:
    service_id = f.readline().strip("\n")


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
