
class NuMailMessage:
    def __init__(self) -> None:
        self.message_stack = []
        self.type = "numail"
        self.numail = {}
        self.email = {}
        self.client_self_id = ""
        self.client_ip = ()
        self.client_username = ""
        self.from_addr = ""
        self.is_send = None
        self.is_client = False
    
    def stack(self) -> list:
        return self.message_stack
    
    def append(self, who:str, content:str) -> None:
        self.message_stack.append([who, content])
    
    def get_type(self) -> str:
        return self.type
    
    def set_type(self, type:str) -> None:
        self.type = type
    
    def details(self) -> dict:
        if self.type == "numail":
            return self.numail
        else:
            return self.email
        
    def set_client_self_id(self, id:str) -> None:
        self.client_self_id = id
    
    def get_client_self_id(self) -> str:
        return self.client_self_id
    
    def set_client_ip(self, ip:tuple) -> None:
        self.client_ip = ip
    
    def get_client_ip(self) -> tuple:
        return self.client_ip
    
    def get_client_username(self) -> str:
        return self.client_username
    
    def set_client_username(self, username:str) -> None:
        self.client_username = username

    def get_from_addr(self) -> str:
        return self.from_addr
    
    def set_from_addr(self, from_addr:str) -> None:
        self.from_addr = from_addr
    
    def get_is_send(self) -> bool | None:
        return self.is_send
    
    def set_is_send(self, bool: bool | None) -> None:
        self.is_send = bool
    
    def get_is_client(self) -> bool | None:
        return self.is_client
    
    def set_is_client(self, bool: bool | None) -> None:
        self.is_client = bool
    
    def get_details(self) -> dict:
        return {
            "message_stack": self.message_stack,
            "type": self.type,
            "numail": self.numail,
            "email": self.email,
            "client_self_id": self.client_self_id,
            "client_ip": self.client_ip,
            "client_username": self.client_username,
            "from_addr": self.from_addr,
            "is_send": self.is_send,
            "is_client": self.is_client
        }