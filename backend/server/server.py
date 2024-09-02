import asyncio
import argparse
import signal

from pathlib import Path

from errors.nuerrors import NuMailError
from logger.logger import NuMailLogger, server_log
from config import server_config, server_settings

async def handle_request(reader, writer):
    pass


async def main():
    servers = []
    for port in server_settings["port"]:
        try:
            server = await asyncio.start_server(handle_request, server_settings["ip"], port)
            servers.append(server)
        except OSError as e:
            if e.errno == 98:
                raise NuMailError(code="7.2.2", message="Port and/or address already in use", other=e)
            else:
                raise NuMailError(code="7.2.1", message=f"Error starting server:\n{e}", other=e)
    
    async with asyncio.TaskGroup() as group:
        for server in servers:
            group.create_task(server.serve_forever())
            if server.is_serving():
                print(f"Server listening on {server.sockets[0].getsockname()[0]}:{server.sockets[0].getsockname()[1]}")
            else:
                raise NuMailError(code="7.2.1", message="Error starting server")


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

        # async def handle_client(reader, writer):
        #     print('New client connected...')
        #     line = str()
        #     while line.strip() != 'quit':
        #         line = (await reader.readline()).decode('utf8')
        #         if line.strip() == '': continue
        #         print(f'Received: {line.strip()}')
        #         writer.write(line.encode('utf8'))
        #     writer.close()
        #     print('Client disconnected...')

        # async def run_server(host, port):
        #     server = await asyncio.start_server(handle_client, host, port)
        #     print(f'Listening on {host}:{port}...')
        #     async with server:
        #         await server.serve_forever()

        # try:
        #     asyncio.run(run_server(host='localhost', port=int(sys.argv[1])))
        # except KeyboardInterrupt:
        #     print("Server stopped.")

        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Server stopped.")
    except NuMailError as e:
        print(e)
    except Exception as e:
        print(f"An error has occured:\n{e}")