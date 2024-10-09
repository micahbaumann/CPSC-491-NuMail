import asyncio

from errors.nuerrors import NuMailError
from server.message.NuMailMessage import NuMailMessage
from server.message.MessageLine import MessageLine
from config.config import server_settings
from logger.logger import NuMailLogger

message_receipt = NuMailLogger("sent.log")



# MODIFY MESSAGE RECEIPT TO WORK FOR THIS




class NuMailRequest:
    async def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.message_info = NuMailMessage()
        self.message_info.set_is_client(True)
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except (ConnectionRefusedError, OSError) as e:
            raise NuMailError(code="7.6.1", message="Cannot connect to server")
    
    async def send(self, message: str) -> str:
        if not self.writer:
            raise NuMailError(code="7.6.2", message="Connection not open")
        else:
            try:
                self.writer.write(MessageLine(message, self.message_info).bytes())
                await self.writer.drain()

                data = await asyncio.wait_for(self.reader.read(int(server_settings["buffer"])), float(server_settings["send_timeout"]))
                return data.decode()
            except asyncio.TimeoutError:
                raise NuMailError(code="7.6.5", message="Connection timeout")
            except ConnectionResetError:
                raise NuMailError(code="7.6.4", message="Connection reset")
            except Exception as e:
                raise NuMailError(code="7.6.0", message="NuMail request error")

    async def open(self, host, port) -> None:
        if self.writer:
            raise NuMailError(code="7.6.2", message="Another connection already open")
        else:
            try:
                self.reader, self.writer = await asyncio.open_connection(host, port)
                self.host = host
                self.port = port
                self.message_info = NuMailMessage()
                self.message_info.set_is_client(True)
            except (ConnectionRefusedError, OSError) as e:
                raise NuMailError(code="7.6.1", message="Cannot connect to server")

    async def close(self) -> None:
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            message_receipt.log(["THIS IS WHERE THE MESSAGE ID WILL GO WHEN IMPLEMENTED", self.message_info.stack()], type=self.message_info.get_type())
            self.reader = self.writer = self.host = self.port = self.message_info = None