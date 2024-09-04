
async def numail_parse(reader, writer, message_stack):
    writer.write(b"numail\r\n")
    await writer.drain()
    message = await reader.read(1024)
    writer.write(f"{message.strip()}\r\n".encode("ascii"))
    await writer.drain()