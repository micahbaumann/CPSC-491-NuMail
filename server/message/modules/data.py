from server.message.server_parser import numail_server_parser
from server.message.MessageLine import MessageLine

@numail_server_parser
async def mod_data(reader, writer, message, local_stack, state, loop):
    loop.trim(False)
    if not state or state["start"] != True:
        loop.continueLoop()
        state["start"] = True
        state["data"] = ""
        return
    else:
        if local_stack[-1] == '.\r\n':
            message.set_payload(state["data"])
            loop.returnLoop()
            writer.write(MessageLine(f"250 2.0.0 Message accepted for delivery", message).bytes())
            await writer.drain()
            return
        else:
            line = local_stack[-1]
            if len(line) > 0 and line[0] == '.':
                line = line[1:]
            
            state["data"] += line
    
    loop.continueLoop()