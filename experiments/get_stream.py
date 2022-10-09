import aiohttp
from toolz import pipe
from asyncio import sleep, create_task, run
from dotenv import load_dotenv
import json

from listener.subscribe import with_items, subscription, with_worlds


async def main():
    load_dotenv()
    url = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:example"
    payload = pipe({}, subscription, with_worlds([10]), with_items)
    run = True

    async def close():
        nonlocal run
        await sleep(900)
        run = False

    print("Connecting...")
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            await ws.send_json(payload)
            print("Connected!")
            create_task(close())

            print("Listening...")
            events = []
            while run:
                res = await ws.receive_json()
                print(res)
                if "payload" in res:
                    events.append(res)

            print("Dumping...")
            with open("results/item_added.json", "w+") as f:
                json.dump({"events": events}, f)
            print("Dumped events")


run(main())
