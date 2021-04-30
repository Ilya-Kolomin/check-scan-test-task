import asyncio
import websockets


async def client():
    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as websocket:
        with open("result.txt", "w") as file:
            while True:
                value = await websocket.recv()
                file.write(value + "\n")
                file.flush()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(client())
