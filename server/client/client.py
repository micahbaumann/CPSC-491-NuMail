import asyncio
import re

from errors.nuerrors import NuMailError
from server.message.NuMailMessage import NuMailMessage
from server.message.MessageLine import MessageLine
from config.config import server_settings
from logger.logger import NuMailLogger

message_receipt = NuMailLogger("sent.log")



# MODIFY MESSAGE RECEIPT TO WORK FOR THIS, TEST EVERYTHING HERE



"""
Creates an new request
"""
class NuMailRequest:
    # async def __init__(self, host, port) -> None:
    #     self.host = host
    #     self.port = port
    #     self.message_info = NuMailMessage()
    #     self.message_info.set_is_client(True)
    #     try:
    #         self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
    #     except (ConnectionRefusedError, OSError) as e:
    #         raise NuMailError(code="7.6.1", message="Cannot connect to server")
    """
    Class init
    Arguments:
    host: host ip/domain to contact
    port: port to contact on
    """
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.message_info = NuMailMessage()
        self.message_info.set_is_client(True)
        self.reader = None
        self.writer = None
    
    """
    Opens a connection
    """
    async def connect(self) -> None:
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            return_data = ""
            data = await asyncio.wait_for(self.reader.read(int(server_settings["buffer"])), float(server_settings["send_timeout"]))
            return_data = data.decode()

            self.message_info.append("server", return_data)
            return return_data
        except (ConnectionRefusedError, OSError) as e:
            raise NuMailError(code="7.6.1", message="Cannot connect to server")
        except asyncio.TimeoutError:
            raise NuMailError(code="7.6.5", message="Connection timeout")
        except ConnectionResetError:
            raise NuMailError(code="7.6.4", message="Connection reset")
        except Exception as e:
            raise NuMailError(code="7.6.0", message="NuMail request error")
    
    """
    Sends a message on an open connection. Returns the response
    Arguments:
    message: a string to send
    """
    async def send(self, message: str) -> str | None:
        if not self.writer:
            raise NuMailError(code="7.6.2", message="Connection not open")
        else:
            try:
                total_size = len(message)
                sent = 0
                while sent < total_size:
                    chunk = message[sent:sent + 74]
                    self.writer.write(MessageLine(chunk, self.message_info).bytes())
                    await self.writer.drain()
                    sent += len(chunk)

                # self.writer.write(MessageLine(message, self.message_info).bytes())
                # await self.writer.drain()
                
                total_return = ""

                data = await asyncio.wait_for(self.reader.read(int(server_settings["buffer"])), float(server_settings["send_timeout"]))
                return_data = data.decode()
                # print(return_data)
                total_return += return_data
                line_data = return_data.split("\r\n")
                while("" in line_data):
                    line_data.remove("")

                for line in line_data:
                    self.message_info.append("server", line)
                # print(f"yess {line_data[-1]} {len(line_data[-1])}")
                # print(line_data)
                while len(line_data[-1]) > 3 and line_data[-1][3] == "-":
                    # print("yesss")
                    data = await asyncio.wait_for(self.reader.read(int(server_settings["buffer"])), float(server_settings["send_timeout"]))
                    return_data = data.decode()
                    # print(return_data)
                    line_data = return_data.split("\r\n")
                    while("" in line_data):
                        line_data.remove("")

                    for line in line_data:
                        self.message_info.append("server", line)
                    
                    total_return += return_data

                return total_return
            except asyncio.TimeoutError:
                raise NuMailError(code="7.6.5", message="Connection timeout")
            except ConnectionResetError:
                raise NuMailError(code="7.6.4", message="Connection reset")
            except Exception as e:
                raise NuMailError(code="7.6.0", message="NuMail request error")
    
    """
    Sends a message on an open connection. Returns nothing
    Arguments:
    message: a string to send
    """
    async def push(self, message: str) -> None:
        if not self.writer:
            raise NuMailError(code="7.6.2", message="Connection not open")
        else:
            try:
                # self.writer.write(MessageLine(message, self.message_info).bytes())
                # await self.writer.drain()
                total_size = len(message)
                sent = 0
                while sent < total_size:
                    chunk = message[sent:sent + 74]
                    self.writer.write(MessageLine(chunk, self.message_info).bytes())
                    await self.writer.drain()
                    sent += len(chunk)
            except asyncio.TimeoutError:
                raise NuMailError(code="7.6.5", message="Connection timeout")
            except ConnectionResetError:
                raise NuMailError(code="7.6.4", message="Connection reset")
            except Exception as e:
                raise NuMailError(code="7.6.0", message="NuMail request error")

    """
    Opens a new connection
    Arguments:
    host: host ip/domain to contact
    port: port to contact on
    """
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

    """
    Closes a connection
    """
    async def close(self) -> None:
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            message_receipt.log(["THIS IS WHERE THE MESSAGE ID WILL GO WHEN IMPLEMENTED", self.message_info.stack()], type=self.message_info.get_type())
            self.reader = self.writer = self.host = self.port = self.message_info = None