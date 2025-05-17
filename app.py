import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from requests_toolbelt.multipart import decoder
from PIL import Image

HOST = '0.0.0.0'
PORT = 8000
UPLOAD_DIR = 'images'
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

class API(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            print('GET home')
        if self.path == '/images':
            print('GET list')
    def do_POST(self):
        if self.path == '/upload':
            print('POST upload')

if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, API)
    print(f"Server started on http://{HOST}:{PORT}")
    httpd.serve_forever()