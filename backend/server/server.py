import asyncio
import argparse

from pathlib import Path

from errors.nuerrors import NuMailError
from config import server_config

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
except NuMailError as e:
    print(e)
except Exception as e:
    print(f"An error has occured:\n{e}")