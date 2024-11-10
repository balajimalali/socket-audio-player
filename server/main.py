import socket
import threading
from module import send_audio_metadata, stream_audio


SERVER_HOST = 'localhost'
SERVER_PORT = 12345
ADDRESS = (SERVER_HOST, SERVER_PORT)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)


server_socket.listen(5)
print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")


clients = []


def handle_client(client_socket, client_address):
    BUFFER_SIZE = 16
    print(f"New connection from {client_address}")
    clients.append(client_socket)
    try:
        message = client_socket.recv(BUFFER_SIZE)
        if not message:
            raise ValueError("No message received")

        print(f"Received from {client_address}: {message.decode()}")

        message = message.decode().strip()

        if message=="Audios":
            print("sending initial data")
            send_audio_metadata(client_socket)
        elif message=="Play":
            print("Play")
            stream_audio(client_socket)
    except ConnectionResetError:
        print(f"Connection lost with {client_address}")
    except:
        print("an error occured")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"Connection closed with {client_address}")


def start_server():
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
        print(f"Active connections: {threading.active_count() - 1}")


start_server()
