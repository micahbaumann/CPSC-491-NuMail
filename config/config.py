from errors.nuerrors import NuMailError

NUMAIL_SERVER_VERSION = "1.0.0"

# Global Config Settings
server_settings = {
    "ip": "127.0.0.1",
    "public_ip": "",
    "domain": "",
    "port": 25,
    "buffer": 1024,
    "read_timeout": 300,
    "send_timeout": 300,
    "dns_timeout": 120,
    "visible_domain": "",
    "attachment_expire": 3600,
    "attachment_delete_on_expire": 1,
}

"""
Sets global config settings from a file
Arguments:
file: the config file name
rules: manully set rules that overide rules in the file
flexrules: manully set rules that rules in the file will overide
"""
def server_config(file, rules={}, flexrules={}):
    try:
        f = open(file, "r")

        server_settings.update(flexrules)
        
        counter = 1
        for line in f:
            clean_line = line.strip()
            if clean_line:
                total_line = ""
                setting = ""
                value = ""
                mode = 0
                for char in clean_line:
                    if char == "#":
                        if total_line == "":
                            mode = 2
                        break
                    elif char == "=":
                        total_line += char
                        if mode == 1:
                            mode = 3
                            break
                        mode = 1
                    elif mode == 0:
                        setting += char
                        total_line += char
                    elif mode == 1:
                        value += char
                        total_line += char
                
                if mode == 1:
                    if value.find(",") >= 0:
                        server_settings[setting] = [s.strip() for s in value.split(",")]
                    else:
                        server_settings[setting] = value
                else:
                    if mode != 2:
                        f.close()
                        raise NuMailError(file=file, line=counter, code="7.1.2", message=f"Syntax error in config file on line {counter}")
            counter += 1

        server_settings.update(rules)
        
        f.close()

    except NuMailError as e:
        raise e
    except Exception as e:
        raise NuMailError(code="7.1.1", message=f"Error opening config file \"{file}\":\n{e}", other=e)