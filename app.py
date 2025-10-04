import os
import socket
import threading
from datetime import datetime
from flask import Flask, request, send_from_directory, jsonify, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode

PORT = 3000
HOST = "0.0.0.0"
app = Flask(__name__, static_folder='static', template_folder='templates')
shared_folder = None
server_thread = None
server_running = False

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_qr(ip, port=PORT, out_path='static/qr.png'):
    url = f'http://{ip}:{port}/'
    img = qrcode.make(url)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list', methods=['GET'])
def api_list():
    if not shared_folder:
        return jsonify({'error': 'No folder selected'}), 400
    rel = request.args.get('path', '')
    target = os.path.normpath(os.path.join(shared_folder, rel))
    if not target.startswith(os.path.abspath(shared_folder)):
        return jsonify({'error': 'Invalid path'}), 400
    items = []
    with os.scandir(target) as it:
        for entry in it:
            stat = entry.stat()
            items.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return jsonify({'path': rel, 'items': items})

@app.route('/download/<path:filepath>')
def download(filepath):
    if not shared_folder:
        return "No folder shared", 400
    target = os.path.normpath(os.path.join(shared_folder, filepath))
    if not target.startswith(os.path.abspath(shared_folder)):
        return "Invalid path", 400
    if os.path.isdir(target):
        return "Cannot download a directory", 400
    directory = os.path.dirname(target)
    filename = os.path.basename(target)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'Missing file', 400
    file = request.files['file']
    dest_path = request.form.get('path', '')
    if file.filename == '':
        return 'No selected file', 400
    filename = secure_filename(file.filename)
    save_dir = os.path.normpath(os.path.join(shared_folder, dest_path))
    if not save_dir.startswith(os.path.abspath(shared_folder)):
        return 'Invalid path', 400
    os.makedirs(save_dir, exist_ok=True)
    file.save(os.path.join(save_dir, filename))
    return 'OK', 200

def start_server_thread():
    global server_thread, server_running
    if server_running:
        return
    def run():
        global server_running
        server_running = True
        ip = get_lan_ip()
        generate_qr(ip, PORT)
        app.run(host=HOST, port=PORT, debug=False)
        server_running = False
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()

class AppGUI:
    def __init__(self, master):
        self.master = master
        master.title('LAN File Server')
        master.geometry('520x380')
        self.frame = tk.Frame(master, padx=12, pady=12)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.folder_label = tk.Label(self.frame, text='No folder selected', anchor='w')
        self.folder_label.pack(fill=tk.X)
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=(8,12))
        self.choose_btn = tk.Button(btn_frame, text='Choose Folder', command=self.choose_folder)
        self.choose_btn.pack(side=tk.LEFT)
        self.start_btn = tk.Button(btn_frame, text='Start Server', command=self.start_server, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(8,0))
        self.stop_btn = tk.Button(btn_frame, text='Stop Server', command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(8,0))
        self.ip_label = tk.Label(self.frame, text='IP: -', anchor='w')
        self.ip_label.pack(fill=tk.X)
        self.port_label = tk.Label(self.frame, text=f'Port: {PORT}', anchor='w')
        self.port_label.pack(fill=tk.X)
        self.qr_label = tk.Label(self.frame, text='QR (not generated)', anchor='center')
        self.qr_label.pack(pady=(12,0))

    def choose_folder(self):
        global shared_folder
        folder = filedialog.askdirectory()
        if not folder:
            return
        shared_folder = os.path.abspath(folder)
        self.folder_label.config(text=f'Sharing: {shared_folder}')
        self.start_btn.config(state=tk.NORMAL)

    def start_server(self):
        if not shared_folder:
            messagebox.showwarning('No folder', 'Please choose a folder first')
            return
        start_server_thread()
        ip = get_lan_ip()
        self.ip_label.config(text=f'IP: {ip}')
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        qr_path = os.path.join(os.getcwd(), 'static', 'qr.png')
        if os.path.exists(qr_path):
            img = Image.open(qr_path).resize((180,180))
            self.qr_imgtk = ImageTk.PhotoImage(img)
            self.qr_label.config(image=self.qr_imgtk, text='')
        else:
            self.qr_label.config(text='QR not ready')
        messagebox.showinfo('Server started', f'Server running\\nLocal: http://localhost:{PORT}\\nLAN: http://{ip}:{PORT}')

    def stop_server(self):
        messagebox.showinfo('Stop server', 'To stop, close this app.')

if __name__ == '__main__':
    root = tk.Tk()
    gui = AppGUI(root)
    root.mainloop()