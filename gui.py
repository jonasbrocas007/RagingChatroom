import socket
import tkinter as tk
import threading
import ips
import json
import pyaudio
import time

voice_chat_active = None
#online_count = 0

current_theme = "dark"
message_entry = 0
chat_display = 0
name_entry = ""

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
SAMPLE_RATE = 44100  # Sampling rate
CHANNELS = 1         # Mono audio
BUFFER_SIZE = 1024   # Buffer size for sending/receiving

# Global variable for the client socket
client_socket = None
audio_socket = None
info_socket = None
audio = pyaudio.PyAudio()
with open("themes.json", "r") as style_file:
    styles = json.load(style_file)


def toggle_voice_chat():
    global voice_chat_active
    voice_chat_active = not voice_chat_active

def capture_info():
    global online_count
    while True:
        try:
            info_msg = info_socket.recv(1024).decode('utf-8')
            if info_msg:
                # Schedule updating the chat display with the new message
                online_count = int(info_msg)
                online_count_label.config(text=f"Online: {online_count}")
        except:
            print("Disconnected from server.")
            break

def capture_audio():
    global voice_chat_active
    stream = None  # Declare stream variable outside the loop

    try:
        while True:
            # Initialize the stream only when voice chat is active
            if voice_chat_active and not stream:
                stream = audio.open(format=FORMAT, rate=SAMPLE_RATE, channels=CHANNELS,
                                    frames_per_buffer=BUFFER_SIZE, input=True)

            # Capture audio only if voice chat is active
            if voice_chat_active:
                try:
                    data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                    audio_socket.sendall(data)
                except (socket.timeout, socket.error) as e:
                    print(f"Error sending audio: {e}")
                    break
            else:
                # Delay to reduce CPU usage when muted
                time.sleep(0.1)

    finally:
        if stream:
            stream.stop_stream()
            stream.close()

# Function to handle receiving audio data from the server
def receive_audio():
    global voice_chat_active
    output_stream = None  # Declare output_stream variable outside the loop

    try:
        while True:
            # Initialize the output stream only when voice chat is active
            if voice_chat_active and not output_stream:
                output_stream = audio.open(format=FORMAT, rate=SAMPLE_RATE, channels=CHANNELS,
                                           frames_per_buffer=BUFFER_SIZE, output=True)

            # Receive and play audio only if voice chat is active
            if voice_chat_active:
                try:
                    audio_data = audio_socket.recv(BUFFER_SIZE)
                    if audio_data:
                        output_stream.write(audio_data)
                except (socket.timeout, socket.error) as e:
                    print(f"Error receiving audio: {e}")
                    break
            else:
                # Delay to reduce CPU usage when muted
                time.sleep(0.1)

    finally:
        if output_stream:
            output_stream.stop_stream()
            output_stream.close()

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
    global client_socket, audio_socket, info_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = ips.confirmed_server_ip  # Replace with actual server IP
    client_socket.connect((server_ip, 9999))

    audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_socket.connect((server_ip, 10000))

    info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info_socket.connect((server_ip, 10001))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    # Start a thread to receive and play audio from the server
    audio_thread = threading.Thread(target=receive_audio)
    audio_thread.daemon = True
    audio_thread.start()

    # Start a thread to capture and send audio to the server
    capture_audio_thread = threading.Thread(target=capture_audio)
    capture_audio_thread.daemon = True
    capture_audio_thread.start()

    receive_info_thread = threading.Thread(target=capture_info)
    receive_info_thread.daemon = True
    receive_info_thread.start()

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
        display_message(f"{username}: {message}")
        message_entry.delete(0, tk.END)

def settings():
    # Create a new top-level window for settings
    global settings_window
    global dark_mode
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    # Add some widgets to the settings window
    dark_mode = tk.Button(settings_window, text="Switch mode dark/light", command=lambda: switch_color())
    dark_mode.pack()
    apply_settings_theme(current_theme)

    # Example setting option (e.g., a checkbox or entry)

def aplly_theme(theme_name):
    theme_styles = styles["themes"][theme_name]
    
    # Apply styles to main window widgets
    root.configure(**theme_styles["root"])
    welcome.configure(**theme_styles["welcome"])
    name_entry.configure(**theme_styles["name_entry"])
    chat_display.configure(**theme_styles["chat_display"])
    message_entry.configure(**theme_styles["message_entry"])
    button.configure(**theme_styles["button"])
    mute_button.configure(**theme_styles["button"])
    online_count_label.configure(**theme_styles["welcome"])
    button_frame.configure(**theme_styles["root"])

    # Apply styles to settings window widgets

def apply_settings_theme(theme_name):
    theme_styles = styles["themes"][theme_name]
    
    settings_window.configure(**theme_styles["settings_window"])
    dark_mode.configure(**theme_styles["dark_mode_settings"])
    # Apply styles to main window widgets

def switch_color():
    global current_theme
    if current_theme == "dark":
        current_theme = "light"
    elif current_theme == "light":
        current_theme = "dark"

    aplly_theme(current_theme)
    apply_settings_theme(current_theme)

def create_main_window():
    global root
    global welcome
    global name_entry
    global chat_frame
    global chat_display
    global scrollbar
    global message_entry
    global image
    global button
    global mute_image
    global mute_button
    global online_count_label
    global button_frame

    ips.first_window()

    root = tk.Tk()
    root.title("Raging totally not racist Chatroom")
    last_row = root.grid_size()[1]

    # Welcome label
    welcome = tk.Label(root, text="Welcome to the Raging totally not racist Chatroom", font=("Comic-Sans", 16))
    welcome.pack()

    # Name entry field for the user to type their name
    name_entry = tk.Entry(root, width=25)
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

    button_frame = tk.Frame(root)
    button_frame.pack(side="bottom", anchor="w")  # Align frame at the bottom-left

    # Load images for the buttons
    image = tk.PhotoImage(file="setting.png")  # Replace with your actual image file path
    mute_image = tk.PhotoImage(file="mute.png")  # Replace with your actual image file path

    # Create and pack the settings button in the frame
    button = tk.Button(button_frame, image=image, command=lambda: settings())
    button.pack(side="left")  

    # Create and pack the mute button in the frame
    mute_button = tk.Button(button_frame, image=mute_image, command=lambda: toggle_voice_chat())
    mute_button.pack(side="left") 

    online_count_label = tk.Label(button_frame, text=f"online: 0", font=("Comic-Sans", 10))
    online_count_label.pack(side="right")





############################################
#              Main program                #
############################################
# Create the main window
create_main_window()
aplly_theme("dark")

# Start the client connection and get the socket
client_socket = start_client()

# Start the Tkinter main loop
root.mainloop()
