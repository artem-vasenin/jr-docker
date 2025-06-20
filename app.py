import os
import json
import time
import logging
import mimetypes

from PIL import Image
from requests_toolbelt.multipart import decoder
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from db import DBManager

postgres_config = {
    "dbname": os.getenv("DB_NAME") or 'images',
    "user": os.getenv("DB_USER") or 'postgres',
    "password": os.getenv("DB_PASSWORD") or 'root',
    "host": os.getenv("DB_HOST") or 'localhost',
    "port": os.getenv("DB_PORT") or '5432',
}

HOST = os.getenv("APP_HOST") or 'localhost'
PORT = int(os.getenv("APP_PORT")) if os.getenv("APP_PORT") else 8000
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or 'images'
LOGS_DIR = os.getenv("LOGS_DIR") or 'logs'
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE")) if os.getenv("MAX_FILE_SIZE") else 5
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif'}
pages = {'/': './static/index.html', '/upload': './static/form.html', '/list-images': './static/images.html'}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# проверка разрешенного расширения
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# Настройки логгера
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=f'{LOGS_DIR}/app.log',
    filemode='a'
)

class ApiServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # отдаем страницу из списка разрешенных роутов
        if self.path in ['/', '/upload', '/list-images']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(pages[self.path], 'rb') as f:
                self.wfile.write(f.read())
        # Получаем список изображений
        elif self.path == '/get-images':
            with DBManager(postgres_config) as db:
                img_list = [{
                    'id': f[0],
                    'filename': f[1],
                    'original_name': f[2],
                    'size': f[3],
                    'upload_time': f[4].strftime('%Y-%m-%d %H:%M:%S'),
                    'file_type': f[5]
                } for f in db.get_list()]
            if len(img_list) == 0:
                self.send_error_response(404, '404 Not Found')
            else:
                try:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"list": img_list}).encode('utf-8'))
                except Exception as e:
                    self.send_error_response(500, f'Ошибка чтения изображений - {str(e)}')
        # получаем статику - стили, скрипты, картинки для фронта
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
        # если приходит пост запрос на загрузку файла
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                saved = []
                filepath = ''

                # Проверяем верный ли формат данных
                if not content_type.startswith('multipart/form-data'):
                    raise ValueError("Content-Type must be multipart/form-data")

                try:
                    multipart_data = decoder.MultipartDecoder(body, content_type)
                except Exception as e:
                    raise ValueError(f"Parsing multipart data - {str(e)}")

                if len(body) <= 0:
                    raise ValueError("Content-Length должен быть больше 0")

                # Проверяем не превышает ли файл допустимый размер
                if len(body) >= (MAX_FILE_SIZE * 1024 * 1024):
                    raise ValueError(f"Content-Length должен быть меньше {MAX_FILE_SIZE}Mb")

                # читаем переданные данные в цикле
                for part in multipart_data.parts:
                    disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
                    if 'filename' not in disposition:
                        continue

                    filename = str(int(time.time() * 1000))
                    original_name = disposition.split('filename="')[1].split('"')[0]
                    filetype = original_name.rsplit('.', 1)[1].lower()
                    file = {
                        'original_name': original_name,
                        'filename': filename,
                        'size': len(body),
                        'file_type': filetype,
                    }

                    filepath = os.path.join(UPLOAD_DIR, f'{filename}.{filetype}')

                    # Пробуем сохранить файл
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(part.content)
                    except Exception as e:
                        self.send_error_response(500, f"Ошибка сохранения файла ({filename}) - {str(e)}")
                        continue

                    # Делаем проверки после сохранения
                    try:
                        with Image.open(filepath) as img:
                            img.load()
                            format = img.format
                            size = img.size
                        if format.lower() not in ALLOWED_EXT:
                            raise ValueError(f'Запрещенный формат ({format})')
                        saved.append(f"{filename} (format: {format}, size: {size})")
                        with DBManager(postgres_config) as db:
                            db.add_file(file)
                    except Exception as e:
                        os.remove(filepath)
                        self.send_error_response(500, f"Не валидный файл ({filename}) - {str(e)}")
                        continue

                if saved:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"path": filepath}).encode('utf-8'))
                    logging.info(f'Успех: Файл ({filepath}) успешно сохранен')
                    print(f'Успех: Файл ({filepath}) успешно сохранен')
            except Exception as e:
                self.send_error_response(500, f'Error saving file: {str(e)}')
    def do_DELETE(self):
        # Удаление файла по его имени
        if self.path == '/images':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                if content_length <= 0:
                    raise ValueError('Content-Length должен быть больше 0')

                body = self.rfile.read(content_length)
                file_id = body.decode('utf-8')

                # Проверяем переданные данные на пустоту
                if not file_id or not file_id.isdigit():
                    raise ValueError('Пустое ID файла')

                with DBManager(postgres_config) as db:
                    item = db.get_by_id(int(file_id))

                # Проверяем переданные данные на соответствие в бд
                if not item:
                    raise ValueError('Файл с таким ID отсутствует')

                filepath = os.path.join(UPLOAD_DIR, os.path.basename(f'{item[1]}.{item[5]}'))

                if os.path.exists(filepath) and os.path.isfile(filepath):
                    os.remove(filepath)
                    with DBManager(postgres_config) as db:
                        db.delete_by_id(int(file_id))
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"deleted": filepath}).encode('utf-8'))
                    logging.info(f'Успех: Файл ({filepath}) успешно удален')
                    print(f'Успех: Файл ({filepath}) успешно удален')
                else:
                    raise ValueError('File is not found')
            except Exception as e:
                self.send_error_response(500, str(e))
    def send_error_response(self, code, message):
        print(f'Ошибка: {message}')
        logging.error(f'Ошибка: {message}')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

if __name__ == '__main__':
    with DBManager(postgres_config) as pg:
        pg.create_table()

    server_address = (HOST, PORT)
    httpd = ThreadingHTTPServer(server_address, ApiServer)
    print(f"Server started on http://{HOST}:{PORT}")
    httpd.serve_forever()
