import uuid
import re
import base64
import quopri

from pathlib import Path

from errors.nuerrors import NuMailError
from server.client.reader import read_numail, init_numail, NuMailRequest
from server.client.dns import resolve_dns, decode_txt

DEBUG_VARS = {}

class Attachment:
    def __init__(self, data: str = "", data_raw = None, content_type: str = "", name: str = "", expire: int | None = None, expireOnRetrieve: bool = False, id: str = "", from_server: str = "") -> None:
        self.expire = expire
        self.expireOnRetrieve = expireOnRetrieve
        self.data_raw = self.content_type = self.name = self.location = None
        self.id = uuid.uuid1().hex
        self.attachments = []
        self.retreive_file = False
        self.from_server = from_server

        if self.from_server and id:
            self.id = id
            self.retreive_file = True
        elif data_raw and content_type and name:
            self.data_raw = data_raw
            self.content_type = content_type
            self.name = name
        else:
            if id:
                self.id = id
            boundary_match = re.search(r'boundary="([^"]+)"', data)
            if not boundary_match:
                parts = [data]
            else:
                boundary = boundary_match.group(1)
                parts = data.split(f'--{boundary}')
            
            i = 0
            for part in parts:
                # Look for the part with the Content-Disposition indicating an attachment
                if 'Content-Disposition: attachment' in part:
                    # Extract the filename
                    filename_match = re.search(r'filename="([^"]+)"', part)
                    filename = filename_match.group(1) if filename_match else "unknown"
                    
                    # Extract the base64 content
                    encoding_match = re.search(r'Content-Transfer-Encoding: base64', part)
                    encoding_match = re.search(r'Content-Transfer-Encoding:\s*([^\s]+)', part)
                    encoding = encoding_match.group(1).lower() if encoding_match else None
                    
                    if encoding_match:
                        # Extract the payload (the actual base64-encoded data)
                        # with open("attch_output.txt", "w") as file:
                        #     file.write(part)
                        # payload_match = re.search(r'.*\r\n\r\n(.*)', part, re.DOTALL)
                        payload_match = part.strip().split("\r\n\r\n", 1)
                        if len(payload_match) == 2:
                            raw_data = payload_match[1].strip()

                            if encoding == 'base64':
                                payload = Attachment.safe_b64decode(raw_data)
                            elif encoding == 'quoted-printable':
                                payload = quopri.decodestring(raw_data)
                            elif encoding in ['7bit', '8bit']:
                                payload = raw_data.encode('utf-8')
                            elif encoding == 'binary':
                                payload = raw_data.encode('latin1')
                            else:
                                raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                            
                            content_type_match = re.search(r'Content-Type:\s*([^\s;]+)', payload_match[0].strip())
                            if content_type_match:
                                contentType = content_type_match.group(1)
                            else:
                                raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                            
                            # with open("attch_output_2.txt", "w") as file:
                            #     file.write(f"'{payload_match[0].strip()}'\r\n'{payload_match[1].strip()}")

                            if i == 0:
                                self.data_raw = payload
                                self.content_type = contentType
                                self.name = filename
                            else:
                                self.attachments.append(Attachment(data_raw=payload, content_type=contentType, name=filename, expire=self.expire, expireOnRetrieve=self.expireOnRetrieve))
                        else:
                            raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                i += 1
        
        if self.data_raw and self.content_type and self.name and not self.retreive_file:
            loop = True
            while loop:
                try:
                    path = Path(__file__).parent.parent.parent / "bucket"
                    path.mkdir(parents=True, exist_ok=True)
                    file_path = path / f"{self.id}_{self.name}"
                    f = open(file_path, "xb")
                    f.write(self.data_raw)
                    f.close()
                    self.location = file_path
                    loop = False
                except FileExistsError:
                    loop = True
                except Exception as e:
                    raise NuMailError(code="7.9.0", message=f"NuMail attachment error, \"{e}\"" )
    
    def __iter__(self):
        return iter(self.attachments)
    
    def __getitem__(self, index):
        return self.attachments[index]
    
    def __len__(self):
        return len(self.attachments)
    
    def __repr__(self):
        return repr(self.attachments)
    
    def __str__(self):
        return str({
            "expire":self.expire,
            "expireOnRetrieve":self.expireOnRetrieve,
            "data_raw":self.data_raw,
            "content_type":self.content_type,
            "name":self.name,
            "location":self.location,
            "id":self.id,
            "attachments":self.attachments,
            "retreive_file":self.retreive_file,
            "from_server":self.from_server,
        })

    async def retreive(self):
        to_mx = []
        try:
            to_dns_results = await resolve_dns(self.from_server, ["MX"])
            to_mx = sorted(to_dns_results["MX"], key=lambda x: x["priority"])
        except:
            pass
        
        
        numail_dns_settings = {}
        try:
            to_dns_results_txt = await resolve_dns(f"_numail.{self.from_server}", ["TXT"])
            for record in to_dns_results_txt["TXT"]:
                numail_dns_settings.update(decode_txt(record["text"]))
        except:
            pass
            
        if "to_port" in DEBUG_VARS.keys():
            to_port = DEBUG_VARS["to_port"]
        elif "port" in numail_dns_settings.keys() and numail_dns_settings["port"].isdigit():
            to_port = int(numail_dns_settings["port"])
        else:
            to_port = 25


        i = 1
        loop_range_size = len(to_mx)
        for domain in to_mx:
            request = NuMailRequest(domain["host"], to_port)
            try:
                await request.connect()
            except NuMailError as e:
                if i == loop_range_size:
                    raise NuMailError(code="7.9.2", message=f"Unable to retrieve attachment, cannot connect to server: {e}" )
                else:
                    i += 1
                    continue
            init = await init_numail(request) # bool

            if init:
                try:
                    atch_ret = await request.send(f"ATCH RETRIEVE: {self.id}")
                    if read_numail(atch_ret)[0] != "250":
                        # print(0)
                        raise
                    print(len('250-Attachment retrieved\r\n250-Content-Type: image/jpeg; name="269 (2020_08_07 21_09_46 UTC).jpeg"\r\n250-Content-Disposition: attachment; filename="269 (2020_08_07 21_09_46 UTC).jpeg"\r\n250-Content-Transfer-Encoding: base64\r\n250-'))
                    print(len(atch_ret))
                    # print(len(atch_ret.split("\r\n")))
                    # print(atch_ret.split("\r\n")[0])
                    with open("attch_output_6.txt", "w") as file:
                        file.write(atch_ret)
                    separated_split = atch_ret.split("\r\n")
                    separated_split.pop(0)
                    separated = [re.sub(r'^.{4}', '', s) for s in separated_split]
                    att = False
                    full = ""
                    for s in separated:
                        full += s
                        full += "\r\n"

                    newAttachment = Attachment(data=full, id=self.id)
                    self.data_raw = newAttachment.data_raw
                    with open("attch_output_3.txt", "w") as file:
                        file.write(full)
                except:
                    raise NuMailError(code="7.9.2", message=f"Unable to retrieve attachment, cannot connect to server" )
            else:
                raise NuMailError(code="7.9.2", message=f"Unable to retrieve attachment, cannot connect to server" )

            await request.close()
            break
    
    @staticmethod
    def safe_b64decode(b64_string):
        padding_needed = len(b64_string) % 4
        if padding_needed:
            b64_string += '=' * (4 - padding_needed)
        return base64.b64decode(b64_string)