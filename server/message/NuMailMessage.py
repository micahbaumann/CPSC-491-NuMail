"""
Holds information about a message.
"""
class NuMailMessage:
    """
    Init funciton
    """
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
        self.mods = []
        self.to_addr = ""
        self.payload = ""
    
    """
    Returns the message stack.
    """
    def stack(self) -> list:
        return self.message_stack
    
    """
    Appends the message stack with a message
    Arguments:
    who: Who is the message from (client/server)
    content: The message itself
    """
    def append(self, who:str, content:str) -> None:
        self.message_stack.append([who, content])
    
    """
    Returns the message type (numail/email)
    """
    def get_type(self) -> str:
        return self.type
    
    """
    Sets the message type
    Arguments:
    type: The type of message (numail/email)
    """
    def set_type(self, type:str) -> None:
        self.type = type
    
    """
    Returns the details dicitonary for the message
    """
    def details(self) -> dict:
        if self.type == "numail":
            return self.numail
        else:
            return self.email
    
    """
    Sets the ID the client identifies itself as
    Arguments:
    id: The ID
    """
    def set_client_self_id(self, id:str) -> None:
        self.client_self_id = id
    
    """
    Returns the ID the client identifies itself as
    """
    def get_client_self_id(self) -> str:
        return self.client_self_id
    
    """
    Sets the IP and port the client is on
    Arguments:
    ip: The IP and port in a tuple the client is running on
    """
    def set_client_ip(self, ip:tuple) -> None:
        self.client_ip = ip
    
    """
    Returns the client IP and port
    """
    def get_client_ip(self) -> tuple:
        return self.client_ip
    
    """
    Gets the username of the client
    """
    def get_client_username(self) -> str:
        return self.client_username
    
    """
    Sets the client's username
    Arguments:
    username: The username
    """
    def set_client_username(self, username:str) -> None:
        self.client_username = username

    """
    Returns the set from address
    """
    def get_from_addr(self) -> str:
        return self.from_addr
    
    """
    Sets the from address
    Arguments:
    from_addr: The from address
    """
    def set_from_addr(self, from_addr:str) -> None:
        self.from_addr = from_addr
    
    """
    Returns is_send
    """
    def get_is_send(self) -> bool | None:
        return self.is_send
    
    """
    Sets is_send
    Arguments:
    bool: If is_send is true.
    """
    def set_is_send(self, bool: bool | None) -> None:
        self.is_send = bool
    
    """
    Returns if this is a client message
    """
    def get_is_client(self) -> bool | None:
        return self.is_client
    
    """
    Sets if this is a client message
    Arguments:
    is_client: If it's a client or not
    """
    def set_is_client(self, bool: bool | None) -> None:
        self.is_client = bool

    """
    Returns a list of mods this message supports
    """
    def get_mods(self) -> bool | None:
        return self.mods
    
    """
    Sets a list of mods this message supports
    Arguments:
    mods: A list of mods
    """
    def set_mods(self, mods:list) -> None:
        self.mods = mods

    """
    Returns the to address
    """
    def get_to_addr(self) -> bool | None:
        return self.to_addr
    
    """
    Sets the to address
    Arguments:
    to_addr: The address
    """
    def set_to_addr(self, to_address:str) -> None:
        self.to_addr = to_address
    
    """
    Returns the to payload
    """
    def get_payload(self) -> bool | None:
        return self.payload
    
    """
    Sets the to payload
    Arguments:
    data: The payload
    """
    def set_payload(self, data:str) -> None:
        self.payload = data
    
    """
    Returns information in this object in a dictionary
    """
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
            "is_client": self.is_client,
            "mods": self.mods,
            "to_addr": self.to_addr,
            "payload": self.payload
        }