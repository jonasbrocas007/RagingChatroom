import tkinter as tk
def set_server_ip(server_ip):
    global confirmed_server_ip
    confirmed_server_ip = server_ip.get()
    root.destroy()
    return confirmed_server_ip

def first_window():
    global root
    root = tk.Tk()
    root.title("Raging totally not racist Chatroom - Input server IP")

    welcome = tk.Label(root, text="Welcome to the Raging totally not racist Chatroom", font = ("Comic-Sans", 16))
    welcome.pack()

    server_ip = tk.Entry(root, width = 50)
    server_ip.insert(0, "26.52.151.38")
    server_ip.pack()

    send_button = tk.Button(root, text="Send", command=lambda: set_server_ip(server_ip))
    send_button.pack(pady=5)
    root.mainloop()