import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os, json
import socket
import qrcode
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
from tkinter import Tk, Label, Button, filedialog
from functools import partial
import json

# Obtén la IP local automáticamente
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# Clase para un servidor que puede detenerse
class StoppableTCPServer(TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_running = True

    def serve_forever(self):
        while self._is_running:
            self.handle_request()

    def stop(self):
        self._is_running = False
        try:
            socket.create_connection(("localhost", self.server_address[1])).close()
        except Exception as e:
            print(f"Error al intentar detener el servidor: {e}")

# Genera el QR dinámicamente
def generate_qr(ip, port, save_path):
    url = f"http://{ip}:{port}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(save_path, "server_qr.png")
    img.save(qr_path)
    print(f"QR generado. Acceso: {url}")
    print(f"El QR fue guardado en {qr_path}.")
    return url, qr_path

# Personalizar la clase de handler para listar los archivos .mp4
# Personalizar la clase de handler para listar los archivos .mp4
class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/videos':
            # Usa la carpeta configurada en self.directory
            video_dir = self.directory
            try:
                # Lista solo los archivos .mp4 y las imágenes (.png, .jpg)
                videos = [f'/{file}' for file in os.listdir(video_dir) if file.endswith('.mp4')]
                images = [f'/{file}' for file in os.listdir(video_dir) if file.endswith(('.png', '.jpg'))]
                response = {"videos": videos, "images": images}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Error: Carpeta no encontrada.')
        else:
            super().do_GET()


def start_server(self):
    if self.server_thread and self.server_thread.is_alive():
        self.qr_label.config(text="El servidor ya está corriendo.")
        return

    ip_address = get_local_ip()
    port = 8000

    # Generar el QR
    url, qr_path = generate_qr(ip_address, port, self.folder_path)
    self.qr_label.config(text=f"Servidor en {url}\nQR guardado en {qr_path}")

    # Crear el handler con la clase personalizada, usando la carpeta seleccionada
    Handler = partial(CustomRequestHandler, directory=self.folder_path)

    # Iniciar el servidor
    self.server = StoppableTCPServer(("", port), Handler)
    self.server_thread = threading.Thread(target=self.server.serve_forever)
    self.server_thread.daemon = True
    self.server_thread.start()

    # Abrir automáticamente la URL en el navegador
    webbrowser.open(url)


def run(server_class=HTTPServer, handler_class=CustomRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor ejecutándose en el puerto {port}")
    httpd.serve_forever()


# GUI principal
class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor QR de Archivos")
        self.server_thread = None
        self.server = None
        self.folder_path = os.getcwd()  # Carpeta actual por defecto

        Label(root, text="Carpeta compartida:").pack(pady=5)
        self.folder_label = Label(root, text=self.folder_path, fg="blue")
        self.folder_label.pack(pady=5)

        Button(root, text="Seleccionar Carpeta", command=self.select_folder).pack(pady=5)
        Button(root, text="Iniciar Servidor", command=self.start_server).pack(pady=5)
        Button(root, text="Detener Servidor", command=self.stop_server).pack(pady=5)

        self.qr_label = Label(root, text="", fg="green")
        self.qr_label.pack(pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_path)
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=self.folder_path)

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.qr_label.config(text="El servidor ya está corriendo.")
            return

        ip_address = get_local_ip()
        port = 8000

        # Generar el QR
        url, qr_path = generate_qr(ip_address, port, self.folder_path)
        self.qr_label.config(text=f"Servidor en {url}\nQR guardado en {qr_path}")

        # Crear el handler con la clase personalizada
        Handler = partial(CustomRequestHandler, directory=self.folder_path)

        # Iniciar el servidor
        self.server = StoppableTCPServer(("", port), Handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Abrir automáticamente la URL en el navegador
        webbrowser.open(url)

    def stop_server(self):
        if self.server:
            self.server.stop()  # Detener el servidor
            self.server_thread.join()  # Esperar a que el hilo termine
            self.server = None
            self.server_thread = None
            self.qr_label.config(text="Servidor detenido.")
            print("Servidor detenido correctamente.")
        else:
            self.qr_label.config(text="No hay servidor corriendo.")

if __name__ == "__main__":
    root = Tk()
    app = ServerApp(root)
    root.mainloop()
