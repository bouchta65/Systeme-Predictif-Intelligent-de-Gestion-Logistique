import random
import asyncio
import json
import websockets

async def generate_data():
    async with websockets.serve(send_data, "0.0.0.0", 8765):
        await asyncio.Future()  

async def send_data(websocket):
    while True:
        data = {
            "order_id": random.randint(1000, 9999),
            "value": random.random()*100,
            "status": random.choice(["delivered", "late"])
        }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(generate_data())
