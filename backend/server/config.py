from errors.nuerrors import NuMailError

# Global Config Settings
server_settings = {
    "ip": "127.0.0.1",
    "port": 7777,
}

"""
Sets global config settings from a file
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
                setting = ""
                value = ""
                mode = 0
                for char in clean_line:
                    if char == "#":
                        mode = 4
                        break
                    elif char == "=":
                        if mode == 1:
                            mode = 3
                            break
                        mode = 1
                    elif mode == 0:
                        setting += char
                    elif mode == 1:
                        value += char
                
                if mode == 1:
                    if value.find(",") > 0:
                        value = [s.strip() for s in value.split(",")]
                    server_settings[setting] = value
                else:
                    if not mode == 4:
                        f.close()
                        raise NuMailError(file=file, line=counter, code="7.1.2", message=f"Syntax error in config file on line {counter}")
            counter += 1

        server_settings.update(rules)
        
        f.close()

    except NuMailError as e:
        raise e
    except Exception as e:
        raise NuMailError(code="7.1.1", message=f"Error opening config file \"{file}\":\n{e}", other=e)