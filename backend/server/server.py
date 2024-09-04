import asyncio
import argparse
import signal
import ast

from pathlib import Path

from errors.nuerrors import NuMailError
from logger.logger import server_log
from config import server_config, server_settings, NUMAIL_SERVER_VERSION
from messagelib.MessageLine import MessageLine

"""
Handles the input and output of incoming requests
Arguments:
reader: asyncio reader object
writer: asyncio writer object
"""
async def handle_request(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection: {addr}")
    server_log.log(f"New connection: {addr}")

    if "domain" in server_settings and server_settings["domain"]:
        server_self = server_settings["domain"]
    elif "public_ip" in server_settings and server_settings["public_ip"]:
        server_self = server_settings["public_ip"]
    else:
        server_self = server_settings["ip"]
    
    writer.write(MessageLine(f"220 {server_self} NuMail Server {NUMAIL_SERVER_VERSION}").bytes())
    await writer.drain()

    while True:
        try:
            data = await asyncio.wait_for(reader.read(int(server_settings["buffer"])), float(server_settings["read_timeout"]))
            message = data.decode("ascii")
            if not message:
                print(f"Connection from {addr} closed")
                break

            if message.strip() == "QUIT".strip():
                print(f"Connection from {addr} closed")
                break

            # print(f"Received {message} from {addr}")
            # response = f"Echo: {message}"
            # writer.write(response.encode("ascii"))
            # await writer.drain()
        except TimeoutError:
            writer.write(MessageLine("500 Connection timed out").bytes())
            await writer.drain()
            server_log.log(f"Connection {addr} timeout", type="request_warning")
            break
        except UnicodeDecodeError as e:
            writer.write(MessageLine("500 Invalid character").bytes())
            await writer.drain()
            server_log.log(f"Connection {addr} invalid character", type="request_error")
            break
        except Exception as e:
            writer.write(MessageLine("500 Unexpected error").bytes())
            await writer.drain()
            server_log.log(f"Connection {addr}:\n{e}", type="request_error")
            break

        
    writer.write(MessageLine("221 Closing").bytes())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    server_log.log(f"Connection {addr} closed")
    print(f"Connection {addr} closed")


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

"""
Starts a new server listening on the port and IP provided
Arguments:
ip: the ip to run the server on
port: the port to run the server on
"""
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

"""
Safely shuts down all servers.
Arguments:
servers: a list of asyncio tasks
"""
def shutdown_handler(servers):
        print(f"\nShutting down...")
        server_log.log(f"Shutting down")
        for server in servers:
            server.cancel()

"""
The main function that controls the server
"""
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


# Main Code
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