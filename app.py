import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from requests_toolbelt.multipart import decoder
from PIL import Image
import time

HOST = '0.0.0.0'
PORT = 8000
UPLOAD_DIR = 'images'
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)
files = {'/': './static/index.html', '/upload': './static/form.html', '/images': './static/images.html'}

class API(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path in ['/', '/upload', '/images']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(files[self.path], 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/css/') or self.path.startswith('/js/') or self.path.startswith('/img/'):
            file_path = './static' + self.path
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
        elif self.path == '/images':
            print('GET list')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    def do_POST(self):
        def send_err(text, status=400):
            self.send_response(status)
            self.end_headers()
            self.wfile.write(text)

        if self.path == '/upload':
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers.get('Content-Length', 0))

            if not content_type.startswith('multipart/form-data'):
                send_err(b"Error: Content-Type must be multipart/form-data")
                return

            if content_length <= 0:
                send_err(b"Error: Content-Length must be greater than 0")
                return

            body = self.rfile.read(content_length)

            try:
                multipart_data = decoder.MultipartDecoder(body, content_type)
            except Exception as e:
                send_err(f"Error parsing multipart data: {str(e)}".encode('utf-8'))
                return

            saved = []
            errors = []

            for part in multipart_data.parts:
                disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
                if 'filename' not in disposition:
                    continue

                # Извлекаем имя файла из Content-Disposition
                filename = disposition.split('filename="')[1].split('"')[0]
                ext = filename.rsplit('.', 1)[-1]
                filename = os.path.basename(f'{int(time.time() * 1000)}.{ext}')
                filepath = os.path.join(UPLOAD_DIR, filename)

                # Сохраняем файл
                try:
                    with open(filepath, 'wb') as f:
                        f.write(part.content)
                except Exception as e:
                    errors.append(f"{filename}: failed to save file ({str(e)})")
                    continue

                # Проверяем, является ли файл изображением
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                    with Image.open(filepath) as img:
                        format = img.format
                        size = img.size
                    saved.append(f"{filename} (format: {format}, size: {size})")
                except Exception as e:
                    print(f'{e.__class__.__name__}: {e}')
                    os.remove(filepath)
                    errors.append(f"{filename}: not a valid image, removed")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = f'{{"path": "{filepath}"}}'

            # response = ""
            # if saved:
                # response += "Uploaded and verified images:\n" + "\n".join(saved) + "\n"
            # if errors:
                # response += "Errors:\n" + "\n".join(errors)

            self.wfile.write(response.encode('utf-8'))

    def do_DELETE(self):
        if self.path == '/images':
            print('Delete')

if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, API)
    print(f"Server started on http://{HOST}:{PORT}")
    httpd.serve_forever()