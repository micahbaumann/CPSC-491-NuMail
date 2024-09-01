import socket

def start_second_user_server():
    host = '0.0.0.0'
    port = 8888
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Second user's server listening on {host}:{port}")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                if not data:
                    break
                info = data.decode()
                print(f"Received info to verify: {info}")
                
                # For simplicity, just echo back the received info
                response = f"Verified: {info}"
                conn.sendall(response.encode())

if __name__ == "__main__":
    start_second_user_server()