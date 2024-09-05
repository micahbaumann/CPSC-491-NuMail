import asyncio

# from MessageLine import MessageLine
# from NuMailMessage import NuMailMessage

async def numail_parse(reader, writer, message_stack):
    writer.write(b"numail\r\n")
    await writer.drain()
    message = await reader.read(1024)
    writer.write(f"{message.strip()}\r\n".encode("ascii"))
    await writer.drain()

    # addr = message_stack.get_client_ip()
    # while True:
    #     try:
    #         data = await asyncio.wait_for(reader.read(int(server_settings["buffer"])), float(server_settings["read_timeout"]))
    #         message = data.decode("ascii")
    #         message_stack.append("client", message)
    #         trim_message = message.strip()
    #         if not message:
    #             print(f"Connection from {addr[0]} port {addr[1]} closed")
    #             break

            
    #     except TimeoutError:
    #         writer.write(MessageLine("500 Connection timed out", message_stack).bytes())
    #         await writer.drain()
    #         server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
    #         break
    #     except UnicodeDecodeError as e:
    #         writer.write(MessageLine("500 Invalid character", message_stack).bytes())
    #         await writer.drain()
    #         server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
    #         break
    #     except Exception as e:
    #         writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
    #         await writer.drain()
    #         server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
    #         break

async def email_parse(reader, writer, message_stack):
    writer.write(b"email\r\n")
    await writer.drain()
    msg = await reader.read(1024)
    writer.write(f"{msg.strip()}\r\n".encode("ascii"))
    await writer.drain()