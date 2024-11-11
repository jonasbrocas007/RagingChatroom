import socket
import threading
import select

# List to store all connected client sockets and their associated usernames/IPs
clients = []
audio_clients = []
info_clients = []

def audio_broadcast(audio_data, sender_audio_socket):
    """ Broadcast audio data to all clients except the sender """
    for audio_client in audio_clients:
        if audio_client != sender_audio_socket:
            try:
                #print(f"Broadcasting audio data to {audio_client}")
                audio_client.send(audio_data)
            except Exception as e:
                print(f"Error sending audio data to {audio_client}: {e}")
                audio_client.close()
                audio_clients.remove(audio_client)

def info_broadcast(infodata):
    for info_client in info_clients:
        try:
            info_client.send(str(infodata).encode('utf-8'))
        except Exception as e:
            print(f"Error sending audio data to {info_client}: {e}")
            info_client.close()
            info_clients.remove(info_client)

def broadcast(message, client_socket):
    """ Broadcast a message to all clients except the sender """
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to {client}: {e}")
                client.close()
                clients.remove(client)

def handle_client(client_socket, client_address, audio_socket, info_socket):
    """ Handle communication with a single client """
    try:
        while True:
            read_sockets, _, _ = select.select([audio_socket, client_socket, info_socket], [], [], 0.1)
            
            for socket in read_sockets:
                if socket == audio_socket:
                    audio_data = socket.recv(1024)
                    if audio_data:
                        audio_broadcast(audio_data, audio_socket)
                    else:
                        break
                elif socket == client_socket:
                    msg = socket.recv(1024).decode('utf-8')
                    if msg.lower() == 'quit':  # Check if client wants to quit
                        break

                    if msg.startswith("USER:"):
                        parts = msg.split("|")
                        username = parts[0].split(":")[1]
                        chat_message = parts[1].split(":")[1]
                        
                        formatted_message = f"{username}: {chat_message}"
                        broadcast(formatted_message, client_socket)
                    else:
                        print(f"Invalid message format from {client_address}")
            info_broadcast(len(clients))
                        
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    
    finally:
        client_socket.close()
        audio_socket.close()
        info_socket.close()
        clients.remove(client_socket)
        audio_clients.remove(audio_socket)
        info_clients.remove(info_socket)


def start_server():
    """ Set up and start the server """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "26.52.151.38"  # Change this to the server's IP if necessary
    server.bind((server_ip, 9999))
    server.listen(5)  # Allow up to 5 clients to connect at once

    audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_server_ip = "26.52.151.38"  # Change this to the server's IP if necessary
    audio_server.bind((audio_server_ip, 10000))
    audio_server.listen(5)  # Allow up to 5 clients to connect at once

    info_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info_server.bind((server_ip, 10001))
    info_server.listen(5)

    print("Server is listening on ports 9999 (chat) and 10000 (audio)...")

    while True:
        # Accept new audio and chat client connections
        audio_socket, addr = audio_server.accept()
        client_socket, addr = server.accept()  # Accept new client
        info_socket, addr = info_server.accept()
        
        print(f"New connection from {addr}")

        # Add the new client to the clients list
        clients.append(client_socket)
        audio_clients.append(audio_socket)
        info_clients.append(info_socket)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, audio_socket, info_socket))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    start_server()
