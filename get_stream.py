import aiohttp
from toolz import pipe
from asyncio import sleep, create_task, run

from listener.subscribe import with_items, subscription, with_worlds

async def main():
    url = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:example"
    payload = pipe({}, subscription, with_worlds([10]), with_items)
    run = True

    async def close():
        await sleep(10)
        run = False

    with aiohttp.ClientSession as session:
        async with session.ws_connect(url) as ws:
            await ws.send_json(payload)
            create_task(close())
            while run:
                res = await ws.receive_json()
                print(res)

run(main())