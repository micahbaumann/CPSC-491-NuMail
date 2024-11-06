from server.message.server_parser import numail_server_parser
from server.message.MessageLine import MessageLine

@numail_server_parser
async def mod_data(reader, writer, message, local_stack, state, loop):
    loop.trim(False)
    if not state or state["mode"] == None:
        loop.continueLoop()
        state["mode"] = 0
        return
    else:
        print(f"'{local_stack[-1][:-2]}'")
        if local_stack[-1] == '.\r\n':
            loop.returnLoop()
            writer.write(MessageLine(f"250 2.0.0 Message accepted for delivery", message).bytes())
            await writer.drain()