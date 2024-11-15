import uuid

from pathlib import Path
from email import policy
from email.parser import BytesParser

class Attachment:
    def __init__(self, data: str = "", data_raw = None, content_type: str = "", name: str = "", expire: int | None = None, expireOnRetrieve: bool = False) -> None:
        self.data_raw = self.content_type = self.name = self.location = None
        self.attachments = []
        
        if data_raw and content_type and name:
            self.data_raw = data_raw
            self.content_type = content_type
            self.name = name
        else:
            msg = BytesParser(policy=policy.default).parsebytes(data.encode("utf-8"))

            # Walk through each part of the email
            i = 0
            for part in msg.iter_parts():
                # Check if this part is an attachment
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    contentType = part.get_content_type()
                    payload = part.get_payload(decode=True)  # Decode the base64 data
                    
                    if i == 0:
                        self.data_raw = payload
                        self.content_type = contentType
                        self.name = filename
                    else:
                        self.attachments.append(Attachment(data_raw=payload, content_type=contentType, name=filename))
                    i += 1
        
        if self.data_raw and self.content_type and self.name:
            loop = True
            while loop:
                try:
                    file_path = Path(__file__).parent / "bucket" / f"{uuid.uuid1().hex}_{self.name}"
                    f = open(file_path, "x")
                    f.write(self.data_raw)
                    f.close()
                    self.location = file_path
                    loop = False
                except FileExistsError:
                    loop = True
    
    def __iter__(self):
        # This allows the object to be iterable, like a list.
        return iter(self.attachments)
    
    def __getitem__(self, index):
        # Allows indexing like a list.
        return self.attachments[index]
    
    def __len__(self):
        # Allows the use of len() like a list.
        return len(self.attachments)
    
    def __repr__(self):
        # Provides a string representation like a list.
        return repr(self.attachments)