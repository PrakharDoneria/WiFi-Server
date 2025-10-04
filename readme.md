# LAN File Server

A simple and modern solution for sharing files across your local network. This application runs a web server on your computer, allowing any device on the same WiFi network to easily upload and download files through a clean web interface. A desktop GUI makes it easy to start and manage the server.

## Features

  * **Easy Setup**: Run a single Python script to get started.
  * **Desktop GUI**: A simple Tkinter interface to select a folder, start the server, and view connection details.
  * **Modern Web UI**: A responsive and user-friendly web interface built with React and Material-UI for managing files.
  * **QR Code Access**: A QR code is automatically generated for quick access from mobile devices.
  * **File Operations**:
      * Upload files directly from the web interface.
      * Download files with a single click.
      * Search for files by name.
      * Sort files by name, size, or modification date.

## Installation

### Prerequisites

  * Python 3.6+
  * A web browser

### Setup

1.  **Clone or Download:** Get the project files onto your computer.

2.  **Create a Virtual Environment (Recommended):**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:** Install the required Python libraries using the `requirements.txt` file.

    ```sh
    pip install -r requirements.txt
    ```

## How to Run

1.  **Execute the Application:**
    Run the `app.py` script from your terminal:

    ```sh
    python app.py
    ```

2.  **Use the Desktop Controller:**

      * The desktop application window will appear.
      * Click **"Choose Folder"** to select the directory you want to share.
      * Click **"Start Server"**.

3.  **Access the Web Interface:**

      * Once the server is running, the GUI will display the server's local IP address and a QR code.
      * **On a mobile device:** Scan the QR code with your camera to open the web interface.
      * **On any device:** Open a web browser and navigate to the URL shown in the GUI (e.g., `http://192.168.1.10:3000`).

## Project Structure

```
WiFi Server/
├── ui/
│   ├── __init__.py
│   └── gui.py           # The Tkinter desktop GUI code
├── static/
│   ├── css/style.css    # Styles for the web interface
│   ├── js/app.js        # React/JS logic for the web UI
│   └── qr.png           # Auto-generated QR code
├── templates/
│   └── index.html       # The main HTML file for the web UI
├── .gitignore           # Files and folders to ignore in version control
├── app.py               # The main Flask server and application entry point
└── requirements.txt     # Python dependencies
```

## Technologies Used

  * **Backend**: Flask
  * **Desktop GUI**: Tkinter
  * **Frontend**: React, Material-UI (MUI)
  * **QR Code Generation**: `qrcode`
  * **Image Handling**: `Pillow`