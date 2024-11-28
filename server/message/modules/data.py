import re
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
        data_str = local_stack[-1]
        local_loop = False
        parts = re.split(r'(\r\n)', data_str)
        result = []
        temp = ""
        for part in parts:
            temp += part
            if part == '\r\n':
                result.append(temp)
                temp = ""

        if temp:
            result.append(temp)

        if len(result) > 1:
            local_loop = True
            data_str = result

        if local_loop:
            for data_line in data_str:
                if data_line == '.\r\n' or data_line == '.':
                    message.set_payload(state["data"])
                    loop.returnLoop()
                    writer.write(MessageLine(f"250 2.0.0 Message accepted for delivery", message).bytes())
                    await writer.drain()
                    return
                else:
                    line = data_line
                    if len(line) > 0 and line[0] == '.':
                        line = line[1:]
                    
                    state["data"] += line
        else:
            if data_str == '.\r\n' or data_str == '.':
                message.set_payload(state["data"])
                loop.returnLoop()
                writer.write(MessageLine(f"250 2.0.0 Message accepted for delivery", message).bytes())
                await writer.drain()
                return
            else:
                line = data_str
                if len(line) > 0 and line[0] == '.':
                    line = line[1:]
                
                state["data"] += line
    
    loop.continueLoop()