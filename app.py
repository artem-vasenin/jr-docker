import os
import json
import time
import logging
import mimetypes

from PIL import Image
from requests_toolbelt.multipart import decoder
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = '0.0.0.0'
PORT = 8000
UPLOAD_DIR = 'images'
LOGS_DIR = 'logs'
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 1
pages = {'/': './static/index.html', '/upload': './static/form.html', '/images': './static/images.html'}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    filename=f'{LOGS_DIR}/server.log',
    filemode='a'
)

class ApiServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/upload', '/images']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(pages[self.path], 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/get-images':
            try:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                files = [f for f in os.listdir(UPLOAD_DIR) if allowed_file(f)]
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"list": files}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, f'Listing images: {str(e)}')
        elif self.path.startswith('/css/') or self.path.startswith('/js/') or self.path.startswith('/img/'):
            file_path = './static' + self.path
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
        else:
            self.send_error_response(404, '404 Not Found')
    def do_POST(self):
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                saved = []
                filepath = ''

                if not content_type.startswith('multipart/form-data'):
                    raise ValueError("Content-Type must be multipart/form-data")

                try:
                    multipart_data = decoder.MultipartDecoder(body, content_type)
                except Exception as e:
                    raise ValueError(f"Parsing multipart data: {str(e)}")

                if len(body) <= 0:
                    raise ValueError("Content-Length must be greater than 0")

                if len(body) >= (MAX_FILE_SIZE * 1024 * 1024):
                    raise ValueError(f"Content-Length must be less than {MAX_FILE_SIZE}Mb")

                for part in multipart_data.parts:
                    disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
                    if 'filename' not in disposition:
                        continue

                    filename = disposition.split('filename="')[1].split('"')[0]
                    filename = os.path.basename(f'{int(time.time() * 1000)}__name__{filename}')
                    filepath = os.path.join(UPLOAD_DIR, filename)

                    try:
                        with open(filepath, 'wb') as f:
                            f.write(part.content)
                    except Exception as e:
                        self.send_error_response(500, f"{filename}: failed to save file ({str(e)})")
                        continue

                    try:
                        with Image.open(filepath) as img:
                            img.load()
                            format = img.format
                            size = img.size
                        if format.lower() not in ALLOWED_EXT:
                            raise ValueError(f'Unexpected format: {format}')
                        saved.append(f"{filename} (format: {format}, size: {size})")
                    except Exception as e:
                        os.remove(filepath)
                        self.send_error_response(500, f"{filename}: not a valid image")
                        continue

                if saved:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"path": filepath}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(500, f'Error saving file: {str(e)}')
    def do_DELETE(self):
        if self.path == '/images':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                if content_length <= 0:
                    raise ValueError('Content-Length must be greater than 0')

                body = self.rfile.read(content_length)
                filename = body.decode('utf-8')

                if not filename:
                    raise ValueError('Filename is empty')

                filepath = os.path.join(UPLOAD_DIR, os.path.basename(filename))

                if os.path.exists(filepath) and os.path.isfile(filepath):
                    os.remove(filepath)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"deleted": filepath}).encode('utf-8'))
                else:
                    raise ValueError('File is not found')
            except Exception as e:
                self.send_error_response(500, str(e))
    def send_error_response(self, code, message):
        print(f'[ERROR] {code}: {message}')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ApiServer)
    print(f"Server started on http://{HOST}:{PORT}")
    httpd.serve_forever()