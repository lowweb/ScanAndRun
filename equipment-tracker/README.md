# Equipment Tracker - Система учета движения оборудования

## Описание
Веб-приложение для учета движения оборудования (картриджи, компьютерная и оргтехника) с использованием штрих-кодов.

## Структура проекта
```
equipment-tracker/
├── backend/          # Python FastAPI бэкенд
│   ├── main.py       # Основной файл приложения
│   ├── models.py     # SQLAlchemy модели
│   ├── schemas.py    # Pydantic схемы
│   ├── database.py   # Настройки подключения к БД
│   ├── init_db.py    # Инициализация и тестовые данные
│   └── requirements.txt
├── frontend/         # Vue 3 фронтенд
│   ├── src/
│   │   ├── views/    # Страницы приложения
│   │   ├── stores/   # Pinia хранилища
│   │   ├── router/   # Маршрутизация
│   │   └── plugins/  # Vuetify плагин
│   └── package.json
└── README.md
```

## Технологии
- **Frontend**: Vue 3 + Pinia (менеджер состояний) + Vuetify 3 (UI компоненты) + vue-qrcode-reader
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Штрих-коды**: vue-qrcode-reader плагин для сканирования через камеру

## Требования
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ или Docker

## Инструкция по развертыванию

### Шаг 1: Установка базы данных

#### Вариант A: Docker (рекомендуется)
```bash
docker run --name equipment-db \
  -e POSTGRES_USER=equipment_user \
  -e POSTGRES_PASSWORD=equipment_pass \
  -e POSTGRES_DB=equipment_tracker \
  -p 5432:5432 \
  -d postgres:14
```

#### Вариант B: Локальная установка PostgreSQL
1. Установите PostgreSQL 14+
2. Создайте базу данных и пользователя:
```sql
CREATE DATABASE equipment_tracker;
CREATE USER equipment_user WITH PASSWORD 'equipment_pass';
GRANT ALL PRIVILEGES ON DATABASE equipment_tracker TO equipment_user;
```

### Шаг 2: Настройка и запуск бэкенда

```bash
cd /workspace/equipment-tracker/backend

# Создаем виртуальное окружение (рекомендуется)
python -m venv venv

# Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверяем файл .env (должен существовать)
# При необходимости отредактируйте параметры подключения к БД
cat .env

# Запускаем сервер
# База данных будет автоматически инициализирована при первом запуске
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Бэкенд будет доступен по адресу: `http://localhost:8000`
Документация API (Swagger): `http://localhost:8000/docs`

### Шаг 3: Настройка и запуск фронтенда

Откройте новый терминал:

```bash
cd /workspace/equipment-tracker/frontend

# Устанавливаем зависимости (если еще не установлены)
npm install

# Запускаем сервер разработки
npm run dev
```

Фронтенд будет доступен по адресу: `http://localhost:5173`

### Шаг 4: Проверка работы

1. Откройте браузер и перейдите на `http://localhost:5173`
2. Вы должны увидеть главную страницу приложения
3. Проверьте работу всех разделов:
   - Перемещение оборудования
   - История перемещений
   - Оборудование вне работы
   - Оборудование (список и добавление)

## Тестовые данные

При первом запуске база данных автоматически заполняется тестовыми данными:

### Типы оборудования
- Картридж
- Комп. и орг. техника

### Статусы для картриджей
- МОЛ (в работе)
- Заправка
- Склад - на заправку
- Склад - выдача

### Статусы для компьютерной техники
- Склад
- Склад утилизация
- В ремонте
- ИТ отдел
- МОЛ (в работе)
- Перемещение

### Пользователи
- Администратор Системы (роль: admin, ИТ отдел)
- Иван Иванов (роль: user, ИТ отдел)
- Петр Петров (роль: user, Бухгалтерия)
- Мария Сидорова (роль: user, Отдел продаж)

### Департаменты
- ИТ отдел
- Бухгалтерия
- Отдел продаж

### Оборудование (10 единиц)
Примеры:
- Картридж HP LaserJet 1010 (CARTRIDGE001)
- Ноутбук Dell Latitude 5420 (COMP001)
- Монитор LG 24MK430H (COMP002)
- Принтер HP LaserJet Pro M404n (COMP003)

## Основные функции

### 1. Перемещение оборудования
- Выбор типа оборудования (переключатель)
- Сканирование штрих-кодов через камеру или ввод вручную
- Поддержка множественного сканирования
- Выбор нового статуса из списка (зависит от типа оборудования)
- Для статуса "Перемещение" обязательно указание целевого пользователя
- Просмотр списка отсканированного оборудования перед применением
- Автоматическое предложение добавить новое оборудование при сканировании неизвестного ШК

### 2. История перемещений
- Таблица со всеми записями истории
- Фильтрация по параметрам:
  - Название оборудования
  - Пользователь
  - Департамент
  - Период дат (начало и окончание)
- Сортировка по колонкам
- Цветовая индикация статусов

### 3. Оборудование вне работы
- Просмотр оборудования не в статусе "МОЛ"
- Фильтрация по типу оборудования
- Детальная информация по каждому элементу
- История перемещений для выбранного оборудования

### 4. Управление оборудованием
- Список всего оборудования с фильтрами
- Добавление нового оборудования
- Редактирование существующего
- Поиск по штрих-коду

## Переменные окружения

### Backend (.env)
```
DATABASE_URL=postgresql://equipment_user:equipment_pass@localhost:5432/equipment_tracker
SECRET_KEY=your-secret-key-change-in-production
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Продакшн развертывание

### Бэкенд
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Фронтенд
```bash
cd frontend
npm run build
# Файлы сборки будут в dist/
# Разместите их на веб-сервере (nginx, apache)
```

### Пример конфигурации nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## API Endpoints

- `GET /api/departments` - Список департаментов
- `GET /api/roles` - Список ролей
- `GET /api/equipment-types` - Типы оборудования
- `GET /api/statuses?equipment_type_id=X` - Статусы для типа оборудования
- `GET /api/users` - Список пользователей
- `GET /api/equipment` - Список оборудования (с фильтрами)
- `GET /api/equipment/{barcode}` - Получить оборудование по ШК
- `POST /api/equipment` - Добавить оборудование
- `PUT /api/equipment/{id}` - Обновить оборудование
- `GET /api/movement-history` - История перемещений (с фильтрами)
- `POST /api/movement/change-status` - Изменить статус оборудования
- `GET /api/equipment/not-active` - Оборудование вне работы

## Поддержка и развитие

Система расширяема и позволяет добавлять:
- Новые типы оборудования
- Новые статусы
- Новых пользователей и департаменты

Для добавления новых типов оборудования необходимо:
1. Добавить тип в таблицу equipment_types
2. Добавить соответствующие статусы в таблицу statuses
