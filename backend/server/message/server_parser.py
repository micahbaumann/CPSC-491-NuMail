import asyncio

from functools import wraps

from message.MessageLine import MessageLine
from errors.nuerrors import NuMailError
from logger.logger import server_log
from config import server_settings

def numail_server_parser(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        reader = kwargs.get("reader")
        writer = kwargs.get("writer")
        message_stack = kwargs.get("message")

        if reader and writer and message_stack:
            addr = message_stack.get_client_ip()
            local_stack = [message_stack.stack()[-1][0].strip()]
            state = {}
            result = "continue"
            first = True
            while result == "continue" or result == None:
                try:
                    if first == False:
                        data = await asyncio.wait_for(reader.read(int(server_settings["buffer"])), float(server_settings["read_timeout"]))
                        message = data.decode("ascii")
                        message_stack.append("client", message)
                        trim_message = message.strip()
                        local_stack.append(trim_message)
                        if not message:
                            print(f"Connection from {addr[0]} port {addr[1]} closed")
                            break
                    else:
                        first = False
                    
                    result = await func(local_stack=local_stack, state=state, *args, **kwargs)
                    
                except TimeoutError:
                    writer.write(MessageLine("500 Connection timed out", message_stack).bytes())
                    await writer.drain()
                    server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
                    return "exit"
                except UnicodeDecodeError as e:
                    writer.write(MessageLine("500 Invalid character", message_stack).bytes())
                    await writer.drain()
                    server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
                    return "exit"
                except Exception as e:
                    writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
                    await writer.drain()
                    server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
                    return "exit"
            return result
        else:
            raise NuMailError(code="7.3.1", message=f"Required module parameters reader, writer, and/or message not found in {func.__name__}", shutdown=True)
    return wrapper