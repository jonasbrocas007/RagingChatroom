import socket
import threading

# List to store all connected client sockets and their associated usernames/IPs
clients = []

# Function to handle communication with a single client
def handle_client(client_socket, client_address):
    try:
        while True:
            # Receive message from client
            msg = client_socket.recv(1024).decode('utf-8')
            if msg.lower() == 'quit':  # Check if client wants to quit
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
                # Handle unexpected message formats
                print(f"Invalid message format received from {client_address}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Remove the client from the list and close the socket when done
        client_socket.close()
        clients.remove(client_socket)
        print(f"A client has disconnected from {client_address}")

# Function to broadcast a message to all clients except the sender
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                # Handle errors if a client is disconnected
                client.close()
                clients.remove(client)

def audio_broadcast(): # working on it
    pass

# Set up the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "26.52.151.38"  # Change this to the server's IP if necessary
    server.bind((server_ip, 9999))
    server.listen(5)  # Allow up to 5 clients to connect at once

    print("Server is listening on port 9999...")

    while True:
        client_socket, addr = server.accept()  # Accept new client
        print(f"New connection from {addr}")

        # Add the new client to the clients list
        clients.append(client_socket)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.daemon = True
        client_thread.start()

# Run the server
if __name__ == "__main__":
    start_server()
