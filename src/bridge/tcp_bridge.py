import asyncio, websockets, socket

async def websocket_to_tcp_bridge():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 9999))
    server.listen(1)
    server.setblocking(False)
    
    print("TCP Bridge waiting for Spark...")
    loop = asyncio.get_event_loop()
    client, _ = await loop.sock_accept(server)
    print("Spark connected")
    
    try:
        async with websockets.connect("ws://fastapi:8000/ws/orders") as ws:
            async for msg in ws:
                await loop.sock_sendall(client, (msg + "\n").encode())
    finally:
        client.close()
        server.close()

if __name__ == "__main__":
    asyncio.run(websocket_to_tcp_bridge())
