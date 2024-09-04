
class NuMailMessage:
    def __init__(self) -> None:
        self.message_stack = []
        self.type = "numail"
        self.numail = {}
        self.email = {}
        self.client_self_id = ""
    
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