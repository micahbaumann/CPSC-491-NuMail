import asyncio
import argparse
import signal
import ast

from pathlib import Path

from errors.nuerrors import NuMailError
from logger.logger import server_log
from config import server_config, server_settings

from collections import defaultdict

topics = defaultdict(lambda: [])

async def handle_request(reader, writer):
    # Example 1
    # addr = writer.get_extra_info('peername')
    # print(f"New connection: {addr}")
    # server_log.log(f"New connection: {addr}")

    # while True:
    #     data = await reader.read(int(server_settings["buffer"]))
    #     message = data.decode()
    #     if not message:
    #         print(f"Connection from {addr} closed")
    #         break

    #     print(f"Received {message} from {addr}")
    #     response = f"Echo: {message}"
    #     writer.write(response.encode())
    #     await writer.drain()

    # writer.close()
    # await writer.wait_closed()


    # Example 2
    # print('New client connected...')
    # line = str()
    # while line.strip() != 'quit':
    #     line = (await reader.readline()).decode('utf8')
    #     if line.strip() == '': continue
    #     print(f'Received: {line.strip()}')
    #     cmd = ast.literal_eval(line)
    #     if cmd['command'] == 'subscribe':
    #         topics[cmd['topic']].append(writer)
    #     elif cmd['command'] == 'send':
    #         writers = topics[cmd['topic']]
    #         for w in writers:
    #             w.write(line.encode('utf8'))
    # writer.close()
    # print('Client disconnected...')
    pass


async def background_server(ip, port):
    try:
        server = await asyncio.start_server(handle_request, ip, port)
        if server.is_serving():
            print(f"Server listening on {ip} port {port}")
            server_log.log(f"Server listening on {ip} port {port}")
        else:
            raise NuMailError(code="7.2.1", message="Error starting server")
        
    except OSError as e:
        if e.errno == 98:
            raise NuMailError(code="7.2.2", message="Port and/or address already in use", other=e)
        else:
            raise NuMailError(code="7.2.1", message=f"Error starting server:\n{e}", other=e)
        
    try:
        async with server:
            await server.serve_forever()
    finally:
        print(f"Shutdown {ip} port {port}")
        server_log.log(f"Shutdown {ip} port {port}")

def shutdown_handler(servers):
        print(f"\nShutting down...")
        server_log.log(f"Shutting down")
        for server in servers:
            server.cancel()

async def main():
    servers = []
    if isinstance(server_settings["port"], str):
        ports = [server_settings["port"]]
    else:
        ports = server_settings["port"]
        
    for port in ports:
        servers.append(asyncio.create_task(background_server(server_settings["ip"], port)))
    
    server_loop = asyncio.get_running_loop()
    server_loop.add_signal_handler(signal.SIGINT, lambda: shutdown_handler(servers))
    server_loop.add_signal_handler(signal.SIGTSTP, lambda: shutdown_handler(servers))

    try:
        await asyncio.gather(*servers)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        argparser = argparse.ArgumentParser()
        argparser.add_argument("-c", "--config")
        runtime_args = argparser.parse_args()

        if runtime_args.config:
            config_path = Path(runtime_args.config)
            if config_path.exists():
                server_config(config_path)
            else:
                raise NuMailError(code="7.1.1", message=f"Error opening config file \"{config_path.resolve()}\"")
        else:
            config_path = Path(__file__).parent.parent / "config" / "settings.conf"
            if config_path.exists():
                server_config(config_path.resolve())

        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Server stopped.")
        server_log.log("Server stopped")
    except NuMailError as e:
        print(e)
        server_log.log(e, type="error")
    except Exception as e:
        print(f"An error has occurred:\n{e}")
        server_log.log(f"An error has occurred:\n{e}", type="error")