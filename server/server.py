import asyncio
import argparse
import signal
import ast

from pathlib import Path

from errors.nuerrors import NuMailError
from logger.logger import server_log, NuMailLogger
from config.config import server_config, server_settings, NUMAIL_SERVER_VERSION
from server.message.MessageLine import MessageLine
from server.message.message_parse import email_parse, numail_parse
from server.message.NuMailMessage import NuMailMessage

message_receipt = NuMailLogger("messages.log")

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
                    writer.write(MessageLine(f"650 NuMail1.0", message_info).bytes())
                    await writer.drain()
                    parse_end = await numail_parse(reader, writer, message_info)
                else:
                    message_info.set_type("email")
                    parse_end = await email_parse(reader, writer, message_info)

            elif trim_message == "EHLO" or (len(trim_message) > 4 and trim_message[:5] == "EHLO "):
                check_numail = True
                if len(trim_message) > 4:
                    message_info.set_client_self_id(trim_message[4:].strip())
                writer.write(MessageLine(f"250-NUMAIL Hello {message_info.get_client_self_id()}", message_info).bytes())
                writer.write(MessageLine(f"250 AUTH LOGIN", message_info).bytes())
                await writer.drain()

            elif trim_message == "HELO" or (len(trim_message) > 4 and trim_message[:5] == "HELO "):
                message_info.set_type("email")
                parse_end = await email_parse(reader, writer, message_info)
            elif trim_message == "NOOP" or (len(trim_message) > 4 and trim_message[:5] == "NOOP "):
                writer.write(MessageLine(f"250 Ok", message_info).bytes())
                await writer.drain()
            else:
                writer.write(MessageLine("500 Command unrecognized", message_info).bytes())
                await writer.drain()
            
            if parse_end == "exit":
                break
        except TimeoutError:
            writer.write(MessageLine("421 Connection timed out", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
            break
        except UnicodeDecodeError as e:
            writer.write(MessageLine("421 Invalid character", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
            break
        except NuMailError as e:
            writer.write(MessageLine("421 Unexpected error", message_info).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            if e.shutdown == True:
                raise e
            break
        except Exception as e:
            writer.write(MessageLine("421 Unexpected error", message_info).bytes())
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
    except NuMailError as e:
        raise e
        
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
    if isinstance(server_settings["port"], list):
        ports = server_settings["port"]
    else:
        ports = [server_settings["port"]]
        
    for port in ports:
        servers.append(asyncio.create_task(background_server(server_settings["ip"], port)))
    
    server_loop = asyncio.get_running_loop()
    server_loop.add_signal_handler(signal.SIGINT, lambda: shutdown_handler(servers))
    server_loop.add_signal_handler(signal.SIGTSTP, lambda: shutdown_handler(servers))

    try:
        await asyncio.gather(*servers)
    except asyncio.CancelledError:
        pass