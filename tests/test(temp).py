# From Chatgpt

# import asyncio

# async def handle_client(reader, writer):
#     addr = writer.get_extra_info('peername')
#     print(f"Connection from {addr}")

#     while True:
#         data = await reader.read(100)
#         message = data.decode()
#         if not message:
#             print(f"Connection from {addr} closed")
#             break

#         print(f"Received {message} from {addr}")
#         response = f"Echo: {message}"
#         writer.write(response.encode())
#         await writer.drain()

#     writer.close()
#     await writer.wait_closed()

# async def main(host='127.0.0.1', port=8888):
#     server = await asyncio.start_server(handle_client, host, port)
#     addr = server.sockets[0].getsockname()
#     print(f"Serving on {addr}")

#     async with server:
#         await server.serve_forever()

# # Run the server
# try:
#     asyncio.run(main())
# except KeyboardInterrupt:
#     print("Server stopped.")












# import asyncio
# import signal
# import os

# async def handle_client(reader, writer):
#     addr = writer.get_extra_info('peername')
#     print(f"Connection from {addr}")

#     while True:
#         data = await reader.read(100)
#         message = data.decode()
#         if not message:
#             print(f"Connection from {addr} closed")
#             break

#         print(f"Received {message} from {addr}")
#         response = f"Echo: {message}"
#         writer.write(response.encode())
#         await writer.drain()

#     writer.close()
#     await writer.wait_closed()

# async def main(host='127.0.0.1', port=8888):
#     server = await asyncio.start_server(handle_client, host, port)
#     addr = server.sockets[0].getsockname()
#     print(f"Serving on {addr}")

#     # Handle SIGTSTP (Ctrl+Z)
#     loop = asyncio.get_running_loop()
#     for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGTSTP):
#         loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(server, sig)))

#     async with server:
#         await server.serve_forever()

# async def shutdown(server, sig):
#     print(f"Received exit signal {sig.name}... shutting down.")
#     server.close()
#     await server.wait_closed()
#     print("Server closed.")
    
#     # If SIGTSTP, suspend the process after closing the server
#     if sig == signal.SIGTSTP:
#         signal.signal(signal.SIGTSTP, signal.SIG_DFL)  # Reset to default handler
#         os.kill(os.getpid(), signal.SIGTSTP)  # Suspend the process

#     else:
#         asyncio.get_event_loop().stop()

# # Run the server
# try:
#     asyncio.run(main())
# except KeyboardInterrupt:
#     print("Server stopped.")












# NOT FROM CHAT GPT FROM https://superfastpython.com/asyncio-server-background-task/
# import asyncio
# import signal
 
# # handler for client connections
# async def handler(reader, writer):
#     addr = writer.get_extra_info('peername')
#     print(f"Connection from {addr}")

#     while True:
#         data = await reader.read(100)
#         message = data.decode()
#         if not message:
#             print(f"Connection from {addr} closed")
#             break

#         print(f"Received {message} from {addr}")
#         response = f"Echo: {message}"
#         writer.write(response.encode())
#         await writer.drain()

#     writer.close()
#     await writer.wait_closed()
 
# # task for running the server in the background
# async def background_server():
#     # create an asyncio server
#     server = await asyncio.start_server(handler, '127.0.0.1', 8888)
#     # report the details of the server
#     print(server)
#     try:
#         # ensure the server is closed correctly
#         async with server:
#             # accept client connections forever (kill via control-c)
#             await server.serve_forever()
#     finally:
#         print(f'Server closed: serving={server.is_serving()}')
 
# # main coroutine
# async def main():
#     # start and run the server as a background task
#     server_task = asyncio.create_task(background_server())
#     def shutdown_handler():
#         print("Received shutdown signal...")
#         server_task.cancel()

#     loop = asyncio.get_running_loop()
#     loop.add_signal_handler(signal.SIGINT, shutdown_handler)
#     loop.add_signal_handler(signal.SIGTSTP, shutdown_handler)
#     # wait for the server to shutdown
#     try:
#         await server_task
#     except asyncio.CancelledError:
#         pass
 
# # start the asyncio event loop
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Program interrupted, shutting down...")


# FROM CHAT GPT based off of https://superfastpython.com/asyncio-server-background-task/
import asyncio
import signal

# handler for client connections
async def handler(reader, writer):
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

# task for running the server in the background
async def background_server(port):
    # create an asyncio server
    server = await asyncio.start_server(handler, '127.0.0.1', port)
    # report the details of the server
    print(f"Serving on port {port}")
    try:
        # ensure the server is closed correctly
        async with server:
            # accept client connections forever (kill via control-c)
            await server.serve_forever()
    finally:
        print(f'Server on port {port} closed: serving={server.is_serving()}')

# main coroutine
async def main():
    # create tasks for each server
    ports = [7777, 7778, 7779]
    server_tasks = [asyncio.create_task(background_server(port)) for port in ports]

    def shutdown_handler():
        print("Received shutdown signal...")
        for task in server_tasks:
            task.cancel()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown_handler)
    loop.add_signal_handler(signal.SIGTSTP, shutdown_handler)

    # wait for the servers to shutdown
    try:
        await asyncio.gather(*server_tasks)
    except asyncio.CancelledError:
        pass

# start the asyncio event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted, shutting down...")