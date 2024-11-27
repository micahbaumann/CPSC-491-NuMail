from server.message.server_parser import numail_server_parser
from server.message.MessageLine import MessageLine
from server.message.Attachment import Attachment

@numail_server_parser
async def mod_atch(reader, writer, message, local_stack, state, loop, expire=None, expire_on_retrieve=None):
    loop.trim(False)
    if not state or state["start"] != True:
        loop.continueLoop()
        state["start"] = True
        state["data"] = ""
        return
    else:
        data_str = local_stack[-1]
        local_loop = False
        if local_stack[-1].find("\r\n"):
            data_str = local_stack[-1].split("\r\n")
            local_loop = True
        if local_loop:
            for data_line in data_str:
                if data_line == '.\r\n' or data_line == '.':
                    attachment = Attachment(data=state["data"], expire=expire, expireOnRetrieve=expire_on_retrieve)
                    message.attachments.append(attachment)
                    if attachment.attachments:
                        for attch in attachment.attachments:
                            message.attachments.append(attch)
                    loop.returnLoop()
                    num_attch = len(message.attachments)
                    i = 1
                    for attch in message.attachments:
                        if num_attch > 1 and i != num_attch:
                            writer.write(MessageLine(f"250-2.0.0 {attch.id} Attachment uploaded and attached", message).bytes())
                            await writer.drain()
                        else:
                            writer.write(MessageLine(f"250 2.0.0 {attch.id} Attachment uploaded and attached", message).bytes())
                            await writer.drain()
                        i += 1
                    return
                else:
                    line = data_line
                    if len(line) > 0 and line[0] == '.':
                        line = line[1:]
                    
                    state["data"] += line
        else:
            if data_str == '.\r\n':
                attachment = Attachment(data=state["data"], expire=expire, expireOnRetrieve=expire_on_retrieve)
                message.attachments.append(attachment)
                if attachment.attachments:
                    for attch in attachment.attachments:
                        message.attachments.append(attch)
                loop.returnLoop()
                num_attch = len(message.attachments)
                i = 1
                for attch in message.attachments:
                    if num_attch > 1 and i != num_attch:
                        writer.write(MessageLine(f"250-2.0.0 {attch.id} Attachment uploaded and attached", message).bytes())
                        await writer.drain()
                    else:
                        writer.write(MessageLine(f"250 2.0.0 {attch.id} Attachment uploaded and attached", message).bytes())
                        await writer.drain()
                    i += 1
                return
            else:
                line = data_str
                if len(line) > 0 and line[0] == '.':
                    line = line[1:]
                
                state["data"] += line
        
    loop.continueLoop()