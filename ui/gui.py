import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class AppGUI:
    def __init__(self, master, start_server_func, get_ip_func, set_folder_func, get_port_func):
        self.master = master
        self.start_server_func = start_server_func
        self.get_ip_func = get_ip_func
        self.set_folder_func = set_folder_func
        self.port = get_port_func()

        master.title('LAN File Server')
        master.geometry('550x450')
        master.resizable(False, False)

        # Style
        self.style = ttk.Style(master)
        self.style.theme_use('clam') # Use a modern theme
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'))

        # Main frame
        main_frame = ttk.Frame(master, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Folder Selection
        folder_frame = ttk.LabelFrame(main_frame, text="1. Select Shared Folder", padding="10 10 10 10")
        folder_frame.pack(fill=tk.X, expand=True)

        self.folder_label = ttk.Label(folder_frame, text='No folder selected', wraplength=450)
        self.folder_label.pack(fill=tk.X, pady=(0, 5))

        self.choose_btn = ttk.Button(folder_frame, text='Choose Folder', command=self.choose_folder)
        self.choose_btn.pack(anchor='w')

        # Server Control
        control_frame = ttk.LabelFrame(main_frame, text="2. Control Server", padding="10 10 10 10")
        control_frame.pack(fill=tk.X, expand=True, pady=10)

        self.start_btn = ttk.Button(control_frame, text='Start Server', command=self.start_server, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(control_frame, text='Stop & Exit', command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Server Info
        info_frame = ttk.LabelFrame(main_frame, text="3. Access Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_left = ttk.Frame(info_frame)
        info_left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), expand=True)

        self.ip_label = ttk.Label(info_left, text='LAN IP: -')
        self.ip_label.pack(anchor='w', pady=2)
        
        self.port_label = ttk.Label(info_left, text=f'Port: {self.port}')
        self.port_label.pack(anchor='w', pady=2)
        
        self.status_label = ttk.Label(info_left, text='Status: Stopped', foreground='red')
        self.status_label.pack(anchor='w', pady=10)

        self.qr_label = ttk.Label(info_frame, text='Scan to Connect')
        self.qr_label.pack(side=tk.RIGHT)
        self.qr_imgtk = None # To prevent garbage collection

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        abs_folder = os.path.abspath(folder)
        self.set_folder_func(abs_folder) # Use the callback to set the folder in app.py
        self.folder_label.config(text=f'Sharing: {abs_folder}')
        self.start_btn.config(state=tk.NORMAL)

    def start_server(self):
        self.start_server_func()
        ip = self.get_ip_func()
        self.ip_label.config(text=f'LAN IP: {ip}')
        self.status_label.config(text='Status: Running', foreground='green')
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.choose_btn.config(state=tk.DISABLED)

        qr_path = os.path.join(os.getcwd(), 'static', 'qr.png')
        if os.path.exists(qr_path):
            try:
                img = Image.open(qr_path).resize((150, 150))
                self.qr_imgtk = ImageTk.PhotoImage(img)
                self.qr_label.config(image=self.qr_imgtk, text='')
            except Exception as e:
                self.qr_label.config(text='Error loading QR')
        else:
            self.qr_label.config(text='QR not ready')
        
        messagebox.showinfo('Server Started', f'Server is now running.\n\nLAN URL: http://{ip}:{self.port}')

    def stop_server(self):
        if messagebox.askokcancel("Stop Server", "To stop the server, you must close the application. Close now?"):
            self.master.destroy()