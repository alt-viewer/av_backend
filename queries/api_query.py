from yarl import URL

with open("service_id.txt") as f:
    service_id = f.readline().strip("\n")


def query(path: str = None, params: dict = None, webhook: bool = False) -> URL:
    """Construct a PS2 API query."""
    query = params or {}
    full_path = "/streaming" if webhook else "/get/ps2:v2/" + (path or "")
    return URL.build(
        scheme="wss" if webhook else "https",
        host="push.planetside2.com" if webhook else "census.daybreakgames.com",
        path=full_path,
        query={"service-id": service_id, **query},
    )
