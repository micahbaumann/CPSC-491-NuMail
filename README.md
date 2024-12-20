# NuMail

**IMPORTANT**  
To run on restricted ports, authorize python with this in the command line:
```bash
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.12
```

## Start Flask
```bash
flask --app ui run
```

## Start Venv
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
