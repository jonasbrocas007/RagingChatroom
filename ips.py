import tkinter as tk
import json

server_counting_number = 1
server_counting_number_str = ""

with open("themes.json", "r") as style_file:
    styles = json.load(style_file)

with open("server_list.json", "r") as server_file:
    servers = json.load(server_file)

"""def switch_server(event=None):
    global server_counting_number
    global server_counting_number_str
    global server_ip
    server_ip.delete(0, tk.END)

    server_counting_number += 1
    server_counting_number_str = str(server_counting_number)

    server_ip_insert = servers["servers"][server_counting_number_str]
    server_ip.insert(0, server_ip_insert) """

def switch_server(event=None):
    global server_counting_number
    global server_counting_number_str
    global server_ip
    global server_name
    global server_name_label
    server_ip.delete(0, tk.END)

    server_counting_number_str = str(server_counting_number)
    server_info = servers["servers"].get(server_counting_number_str)

    # Check if the server info exists
    if server_info:
        server_name = next(iter(server_info)) 
        ip_address = server_info[server_name].get("ip")  
        server_name_label.configure(text=server_name)


        # Insert the IP address into the entry widget
        if ip_address:
            server_ip.insert(0, ip_address)
        else:
            server_ip.insert(0, "IP not found")

        # Print or store both values as needed
        #print(f"Server Name: {server_name}, IP Address: {ip_address}")
    else:
        #server_ip.insert(0, "No more servers")
        server_counting_number = 0
    server_counting_number += 1

def set_server_ip(server_ip):
    global confirmed_server_ip
    confirmed_server_ip = server_ip.get()
    root.destroy()
    return confirmed_server_ip


def aplly_theme(theme_name):
    global root
    global welcome
    global send_button
    global server_ip
    global choose_button
    theme_styles = styles["themes"][theme_name]

    root.configure(**theme_styles["root"])
    welcome.configure(**theme_styles["welcome"])
    server_ip.configure(**theme_styles["name_entry"])
    send_button.configure(**theme_styles["button"])
    server_name_label.configure(**theme_styles["welcome"])
    choose_button.configure(**theme_styles["button"])


def first_window():
    global welcome
    global send_button
    global root
    global server_ip
    global server_name_label
    global server_counting_number
    global choose_button
    root = tk.Tk()
    root.title("Raging totally not racist Chatroom - Input server IP")

    welcome = tk.Label(root, text="Welcome to the Raging totally not racist Chatroom", font = ("Comic-Sans", 16))
    welcome.pack()

    server_name_label = tk.Label(root, text="server name", font = ("Comic-Sans", 10))
    server_name_label.pack()

    server_ip = tk.Entry(root, width = 50)
    #server_ip.insert(0, "")
    server_ip.pack()

    send_button = tk.Button(root, text="Send", command=lambda: set_server_ip(server_ip))
    send_button.pack(pady=5)

    choose_button = tk.Button(root, text="Choose Server", command=lambda: switch_server())
    choose_button.pack(pady=5)
    switch_server()
    aplly_theme("dark")
    root.mainloop()