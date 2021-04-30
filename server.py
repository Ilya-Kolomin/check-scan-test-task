import time
import threading

import psycopg2
import asyncio
import websockets

# connecting to the database
conn = psycopg2.connect(dbname="CheckScanTask", user="postgres", password="postgres", host="192.168.31.42")
cur = conn.cursor()

# list of open connections
websockets_list = []


# thread that produces data and writes it to the database
def producer_function():
    from random import randrange
    while True:
        cur.execute("INSERT INTO my_table (value) VALUES (%s)", (randrange(1000),))
        conn.commit()
        time.sleep(10)


# consumes values from database and sends it to all open connections
async def consumer_function():
    last_id = 0
    while True:
        cur.execute("SELECT * FROM my_table WHERE id > %s", (last_id,))
        data = cur.fetchall()
        for id, value in data:
            last_id = id
            await asyncio.gather(*map(lambda x: x.send(str(value)), websockets_list))
            await asyncio.sleep(0)
        await asyncio.sleep(3)


# the handler for the connection
async def stream(websocket, path):
    global websockets_list
    websockets_list.append(websocket)
    await websocket.wait_closed()
    websockets_list.remove(websocket)


if __name__ == '__main__':
    start_server = websockets.serve(stream, "localhost", 8766)
    producer_thread = threading.Thread(target=producer_function)

    producer_thread.start()

    asyncio.get_event_loop().run_until_complete(asyncio.gather(start_server, consumer_function()))
    asyncio.get_event_loop().run_forever()
