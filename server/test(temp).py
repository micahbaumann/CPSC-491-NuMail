import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")

    while True:
        data = await reader.read(100)
        message = data.decode()
        if not message:
            print(f"Connection from {addr} closed")
            break

        print(f"Received {message} from {addr}")
        response = f"Echo: {message}"
        writer.write(response.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def main(host='127.0.0.1', port=8888):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

# Run the server
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped.")