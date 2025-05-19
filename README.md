# Java Rush - Docker

## Работа с проектом

Запуск контейнеров проекта  
`docker compose up --build -d`

Остановка контейнеров  
`docker compose down`

Проект доступен по адресу:  
[http://localhost:8080](http://localhost:8080)

---

## Структура проекта
```text
project/
├── app.py                # Основной Python-бэкенд
├── requirements.txt      # Зависимости Python
├── Dockerfile            # Dockerfile для Python-бэкенда
├── docker-compose.yml    # Конфигурация Docker Compose
├── nginx.conf            # Конфигурация Nginx
├── images/               # Папка для хранения загруженных изображений (volume)
├── logs/                 # Папка для логов (volume)
└── static/               # Дополнительные статические файлы (CSS/JS/HTML/IMG)
```

---

## Маршруты (frontend)

`GET /` - Главная страница  
`GET /upload` - Страница формы загрузки изображений  
`GET /images` - Страница списочной формы изображений

## Маршруты (backend)

`GET /get-images` - Получение списка загруженных файлов (вернет json)  
`POST /upload` - Добавление изображения (вернет json c url-om)  
`DELETE /images` - Удаление изображения (вернет json c url-om)



