async def email_parse(reader, writer, message_stack):
    writer.write(b"email\r\n")
    await writer.drain()
    msg = reader.read(1024)