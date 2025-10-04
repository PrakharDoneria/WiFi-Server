import os
import socket
import threading
from datetime import datetime
from flask import Flask, request, send_from_directory, jsonify, render_template
from werkzeug.utils import secure_filename
import qrcode
import tkinter as tk
from ui.gui import AppGUI  # Import the new GUI class

# --- Server Configuration ---
PORT = 3000
HOST = "0.0.0.0"

# --- Flask App Initialization ---
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Shared State (managed via callbacks from the GUI) ---
shared_folder = None
server_thread = None
server_running = False

def set_shared_folder(folder_path):
    """Callback function for the GUI to set the shared folder."""
    global shared_folder
    shared_folder = folder_path

def get_port():
    """Function to provide the port to the GUI."""
    return PORT

# --- Server Logic Functions ---
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

def start_server_thread():
    global server_thread, server_running
    if server_running:
        return
    if not shared_folder:
        print("Error: No shared folder selected.")
        return

    def run_flask():
        global server_running
        server_running = True
        ip = get_lan_ip()
        generate_qr(ip, PORT)
        print(f"Starting server on http://{HOST}:{PORT}")
        app.run(host=HOST, port=PORT, debug=False)
        server_running = False

    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

# --- Flask Routes ---
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
    
    search_term = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'name')
    items = []
    with os.scandir(target) as it:
        for entry in it:
            if search_term and search_term not in entry.name.lower():
                continue
            stat = entry.stat()
            items.append({
                'name': entry.name, 'is_dir': entry.is_dir(),
                'size': stat.st_size, 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    reverse_order = sort_by.endswith('_desc')
    sort_key = sort_by.removesuffix('_desc')

    if sort_key == 'name':
        items.sort(key=lambda x: x['name'].lower(), reverse=reverse_order)
    elif sort_key == 'size':
        items.sort(key=lambda x: x['size'], reverse=reverse_order)
    elif sort_key == 'modified':
        items.sort(key=lambda x: x['modified'], reverse=reverse_order)
    
    # Always keep directories grouped at the top
    items.sort(key=lambda x: not x['is_dir'])

    return jsonify({'path': rel, 'items': items})

@app.route('/download/<path:filepath>')
def download(filepath):
    if not shared_folder: return "No folder shared", 400
    target = os.path.normpath(os.path.join(shared_folder, filepath))
    if not target.startswith(os.path.abspath(shared_folder)): return "Invalid path", 400
    if os.path.isdir(target): return "Cannot download a directory", 400
    return send_from_directory(os.path.dirname(target), os.path.basename(target), as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files: return 'Missing file', 400
    file = request.files['file']
    dest_path = request.form.get('path', '')
    if file.filename == '': return 'No selected file', 400
    filename = secure_filename(file.filename)
    save_dir = os.path.normpath(os.path.join(shared_folder, dest_path))
    if not save_dir.startswith(os.path.abspath(shared_folder)): return 'Invalid path', 400
    os.makedirs(save_dir, exist_ok=True)
    file.save(os.path.join(save_dir, filename))
    return 'OK', 200

# --- Main Application Runner ---
if __name__ == '__main__':
    root = tk.Tk()
    gui = AppGUI(
        master=root,
        start_server_func=start_server_thread,
        get_ip_func=get_lan_ip,
        set_folder_func=set_shared_folder,
        get_port_func=get_port
    )
    root.mainloop()