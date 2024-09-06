import asyncio
import argparse
import signal
import ast

from pathlib import Path

from errors.nuerrors import NuMailError
from logger.logger import server_log, NuMailLogger
from config import server_config, server_settings, NUMAIL_SERVER_VERSION
from message.MessageLine import MessageLine
from message.message_parse import email_parse, numail_parse
from message.NuMailMessage import NuMailMessage

"""
Handles the input and output of incoming requests
Arguments:
reader: asyncio reader object
writer: asyncio writer object
"""
async def handle_request(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr[0]} port {addr[1]}")
    server_log.log(f"New connection from {addr[0]} port {addr[1]}")

    if "domain" in server_settings and server_settings["domain"]:
        server_self = server_settings["domain"]
    elif "public_ip" in server_settings and server_settings["public_ip"]:
        server_self = server_settings["public_ip"]
    else:
        server_self = server_settings["ip"]
    
    # message_stack = []
    message_info = NuMailMessage()
    message_info.set_client_ip(addr)
    writer.write(MessageLine(f"220 {server_self} NuMail Server {NUMAIL_SERVER_VERSION}", message_info).bytes())
    await writer.drain()

    
    check_numail = False
    while True:
        try:
            data = await asyncio.wait_for(reader.read(int(server_settings["buffer"])), float(server_settings["read_timeout"]))
            message = data.decode("ascii")
            message_info.append("client", message)
            trim_message = message.strip()
            if not message:
                print(f"Connection from {addr[0]} port {addr[1]} closed")
                break
            
            parse_end = "continue"
            if trim_message == "QUIT":
                print(f"Connection from {addr[0]} port {addr[1]} closed")
                break
            elif check_numail:
                if trim_message == "NUML" or (len(trim_message) > 4 and trim_message[:5] == "NUML "):
                    message_info.set_type("numail")
                    message_info.details()["client_numail_version"] = trim_message[4:].strip()
                    parse_end = await numail_parse(reader, writer, message_info)
                else:
                    message_info.set_type("email")
                    parse_end = await email_parse(reader, writer, message_info)

            elif trim_message == "EHLO" or (len(trim_message) > 4 and trim_message[:5] == "EHLO "):
                check_numail = True
                if len(trim_message) > 4:
                    message_info.set_client_self_id(trim_message[4:].strip())
                writer.write(MessageLine(f"250 NUMAIL Hello {message_info.get_client_self_id()}", message_info).bytes())
                await writer.drain()

            elif trim_message == "HELO" or (len(trim_message) > 4 and trim_message[:5] == "HELO "):
                message_info.set_type("email")
                parse_end = await email_parse(reader, writer, message_info)
            else:
                writer.write(MessageLine("500 Command unrecognized", message_info).bytes())
                await writer.drain()
            
            if parse_end == "exit":
                break
            # print(f"Received {message} from {addr}")
            # response = f"Echo: {message}"
            # writer.write(response.encode("ascii"))
            # await writer.drain()
        except TimeoutError:
            writer.write(MessageLine("500 Connection timed out", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
            break
        except UnicodeDecodeError as e:
            writer.write(MessageLine("500 Invalid character", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
            break
        except Exception as e:
            writer.write(MessageLine("500 Unexpected error", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            break

        
    writer.write(MessageLine(f"221 2.0.0 {server_self} closing connection", message_info).bytes())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    server_log.log(f"Connection {addr[0]} port {addr[1]} closed")
    print(f"Connection {addr[0]} port {addr[1]} closed")
    message_receipt.log(["THIS IS WHERE THE MESSAGE ID WILL GO WHEN IMPLEMENTED", message_info.stack()], type=message_info.get_type())


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

        message_receipt = NuMailLogger("messages.log")

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