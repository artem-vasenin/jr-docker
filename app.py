import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from requests_toolbelt.multipart import decoder
from PIL import Image

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
        if self.path == '/upload':
            print('POST upload')
    def do_DELETE(self):
        if self.path == '/images':
            print('Delete')

if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, API)
    print(f"Server started on http://{HOST}:{PORT}")
    httpd.serve_forever()