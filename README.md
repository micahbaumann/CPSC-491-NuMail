# NuMail

**IMPORTANT**  
To run on restricted ports, authorize python with this in the command line:
```bash
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.12
```

**IMPORTANT**
Remember to remove debug dictionaries from each file

**IMPORTANT**
Remember add email spoofing IP checks

## To Run DNS Server
1. 
    ```
    sudo nano /etc/resolv.conf
    ```
2. Uncomment
    ```
    nameserver 127.0.0.1
    ```

## Base64 Username and Password
Username: `bWljYWg=`  
Password: `MTIzNDU=`