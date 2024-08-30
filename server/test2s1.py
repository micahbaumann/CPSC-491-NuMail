import socket

def verify_with_second_user(info):
    second_user_host = '127.0.0.1'  # Change to second user's IP address
    second_user_port = 8888
    
    # Connect to the second user's server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as second_socket:
        second_socket.connect((second_user_host, second_user_port))
        second_socket.sendall(info.encode())  # Send the info to the second user
        response = second_socket.recv(1024)  # Receive the response from the second user
    return response.decode()

def handle_first_user(conn):
    with conn:
        data = conn.recv(1024)
        if not data:
            return
        info = data.decode()
        print(f"Received info: {info}")
        
        # Verify with the second user's server
        verified_info = verify_with_second_user(info)
        
        # Send the verified info back to the first user
        conn.sendall(verified_info.encode())

def start_first_user_server():
    host = '0.0.0.0'
    port = 8889
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"First user's server listening on {host}:{port}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            handle_first_user(conn)

if __name__ == "__main__":
    start_first_user_server()