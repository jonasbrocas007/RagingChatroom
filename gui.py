import socket
import tkinter as tk
import threading
import ips
message_entry = 0
chat_display = 0
name_entry = ""

# Global variable for the client socket
client_socket = None

# Function to handle receiving messages and updating the chat display
def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                # Schedule updating the chat display with the new message
                chat_display.after(0, display_message, msg)
        except:
            print("Disconnected from server.")
            break

# Function to display messages in the chat display Text widget
def display_message(msg):
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"{msg}\n")
    chat_display.yview(tk.END)
    chat_display.config(state=tk.DISABLED)

# Set up the client connection and start the receiving thread
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = ips.confirmed_server_ip  # Replace with actual server IP
    client_socket.connect((server_ip, 9999))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    return client_socket

# Function to send a message along with the username and IP address to the server
def send_message(event=None):
    global client_socket
    
    # Get the username and message input from the user
    username = name_entry.get()
    message = message_entry.get()

    # Get the client's IP address (local machine's IP)
    client_ip = socket.gethostbyname(socket.gethostname())

    if username and message:
        # Format the message to send the username and IP address along with the message
        full_message = f"USER:{username}|MSG:{message}"
        client_socket.send(full_message.encode('utf-8'))

        # Display the sent message in the chat window
        display_message(f"You: {message}")
        message_entry.delete(0, tk.END)

# Create the main window
ips.first_window()

root = tk.Tk()
root.title("Raging totally not racist Chatroom")

# Welcome label
welcome = tk.Label(root, text="Welcome to the Raging totally not racist Chatroom", font = ("Comic-Sans", 16))
welcome.pack()

# Name entry field for the user to type their name
name_entry = tk.Entry(root, width = 25)
name_entry.insert(0, "username")
name_entry.pack()

# Create a frame for the chat display area and the scrollbar
chat_frame = tk.Frame(root)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a Text widget to display the chat messages
chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=15, width=50, state=tk.DISABLED)
chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a Scrollbar for the chat display
scrollbar = tk.Scrollbar(chat_frame, command=chat_display.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Link the scrollbar to the Text widget
chat_display.config(yscrollcommand=scrollbar.set)

# Create an entry box to type new messages
message_entry = tk.Entry(root, width=50)
message_entry.pack(padx=10, pady=5)

message_entry.bind("<Return>", send_message)
# Create a button to send the message
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

# Start the client connection and get the socket
client_socket = start_client()

# Start the Tkinter main loop
root.mainloop()

