
async def numail_parse(reader, writer, message_stack):
    writer.write(b"numail\r\n")
    await writer.drain()
    msg = reader.read(1024)