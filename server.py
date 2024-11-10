import socket
import threading
import select

# List to store all connected client sockets and their associated usernames/IPs
clients = []
audio_clients = []

def audio_broadcast(audio_data, sender_audio_socket):
    """ Broadcast audio data to all clients except the sender """
    for audio_client in audio_clients:
        if audio_client != sender_audio_socket:
            try:
                print(f"Broadcasting audio data to {audio_client}")
                audio_client.send(audio_data)
            except Exception as e:
                print(f"Error sending audio data to {audio_client}: {e}")
                audio_client.close()
                audio_clients.remove(audio_client)

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

def handle_client(client_socket, client_address, audio_socket):
    """ Handle communication with a single client """
    try:
        while True:
            # Use select to handle both audio and chat in non-blocking way
            read_sockets, _, _ = select.select([audio_socket, client_socket], [], [], 0.1)
            
            for socket in read_sockets:
                if socket == audio_socket:
                    audio_data = socket.recv(1024)
                    if audio_data:
                        print(f"Received audio data from {client_address}")
                        audio_broadcast(audio_data, audio_socket)
                    else:
                        print(f"Audio socket closed from {client_address}")
                        break  # Client disconnected
                elif socket == client_socket:
                    msg = socket.recv(1024).decode('utf-8')
                    if msg.lower() == 'quit':  # Check if client wants to quit
                        print(f"Client {client_address} requested to quit")
                        break

                    # Parse the message to extract the username, IP, and message
                    if msg.startswith("USER:"):
                        parts = msg.split("|")
                        username = parts[0].split(":")[1]  # Extract the username
                        chat_message = parts[1].split(":")[1]  # Extract the message
                        
                        # Broadcast the message with the username and IP
                        formatted_message = f"{username}: {chat_message}"
                        broadcast(formatted_message, client_socket)
                    else:
                        print(f"Invalid message format received from {client_address}")

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    
    finally:
        # Remove the client from the list and close the socket when done
        print(f"Disconnecting client {client_address}")
        client_socket.close()
        audio_socket.close()
        clients.remove(client_socket)
        audio_clients.remove(audio_socket)
        print(f"Client {client_address} disconnected")

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

    print("Server is listening on ports 9999 (chat) and 10000 (audio)...")

    while True:
        # Accept new audio and chat client connections
        audio_socket, addr = audio_server.accept()
        client_socket, addr = server.accept()  # Accept new client
        print(f"New connection from {addr}")

        # Add the new client to the clients list
        clients.append(client_socket)
        audio_clients.append(audio_socket)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, audio_socket))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    start_server()
