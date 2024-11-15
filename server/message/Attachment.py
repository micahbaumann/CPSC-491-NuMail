import uuid
import re
import base64
import quopri

from pathlib import Path

from errors.nuerrors import NuMailError

class Attachment:
    def __init__(self, data: str = "", data_raw = None, content_type: str = "", name: str = "", expire: int | None = None, expireOnRetrieve: bool = False) -> None:
        self.data_raw = self.content_type = self.name = self.location = None
        self.id = uuid.uuid1().hex
        self.attachments = []
        
        if data_raw and content_type and name:
            self.data_raw = data_raw
            self.content_type = content_type
            self.name = name
        else:
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
                        payload_match = re.search(r'\r\n\r\n(.*)', part, re.DOTALL)
                        if payload_match:
                            raw_data = payload_match.group(1).strip()

                            if encoding == 'base64':
                                payload = base64.b64decode(raw_data)
                            elif encoding == 'quoted-printable':
                                payload = quopri.decodestring(raw_data)
                            elif encoding in ['7bit', '8bit']:
                                payload = raw_data.encode('utf-8')
                            elif encoding == 'binary':
                                payload = raw_data.encode('latin1')
                            else:
                                raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                            
                            content_type_match = re.search(r'Content-Type:\s*([^\s;]+)', data)
                            if content_type_match:
                                contentType = content_type_match.group(1)
                            else:
                                raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                            
                            if i == 0:
                                self.data_raw = payload
                                self.content_type = contentType
                                self.name = filename
                            else:
                                self.attachments.append(Attachment(data_raw=payload, content_type=contentType, name=filename))
                        else:
                            raise NuMailError(code="7.9.0", message=f"NuMail attachment error")
                i += 1
        
        if self.data_raw and self.content_type and self.name:
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