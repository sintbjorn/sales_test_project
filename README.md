## Структура
```
sales_test_project/
├── sql/
│   └── task_1_sql.sql
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   └── index.html
└── google_sheets/
    ├── SHEETS.md
    └── updateSalesReport.gs
```

---
## 1) SQL
Файл: `sql/task_1_sql.sql` — один запрос (PostgreSQL) с:
- Топ-3 городами по продажам за каждый месяц
- Долей города в месяце (в %)
- Нарастающим итогом по городам

**Как проверить:** создайте таблицы `sales`, `users`, `products` (как в условии), наполните тестовыми данными, выполните запрос в psql/DB GUI.

---
## 2) Backend (FastAPI)
Файлы: `backend/main.py`, `backend/requirements.txt`

### Запуск
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Откройте:  
`http://127.0.0.1:8000/sales/summary?start_date=2025-10-01&end_date=2025-10-14`

**Что делает API**
- Асинхронно тянет `https://jsonplaceholder.typicode.com/posts`
- Превращает посты в «суммы» и раскладывает по дням диапазона
- Считает 3-дневное скользящее среднее и топ-5 дней по продажам
- Валидирует даты и корректно сообщает об ошибках

---
## 3) Frontend (HTML + JS + Chart.js)
Файл: `frontend/index.html`

Просто откройте в браузере. Если API на другом хосте/порте — поправьте `API_BASE` в начале скрипта.

Функциональность:
- Поля выбора дат + кнопка «Получить данные»
- Таблица с сортировкой по клику
- Линейный график продаж и скользящего среднего

---
## 4) Google Sheets + Apps Script
См. `google_sheets/SHEETS.md` и `google_sheets/updateSalesReport.gs`.

Кратко:
- Вставьте формулы QUERY/ARRAYFORMULA/% of Total (см. SHEETS.md)
- В Apps Script вставьте `updateSalesReport.gs`, поменяйте email, запустите функцию.

---
## Заметки разработчика (почему так)
- Я сохранял баланс между «быстро собрать» и «оставить чистый код». Комментарии оставлены с расчётом, что другой человек сможет быстро разобраться.
- В бэкенде ограничил диапазон 365 дней и дал дружелюбные ошибки — это уменьшает риск «залипания» при неправильном вводе.
- В фронтенде не использовал фреймворки — для теста достаточно «ванильного» JS.

---
## 5) Docker (frontend + backend)
Быстрый старт:
```bash
docker compose build
docker compose up
```
Откройте фронтенд: http://localhost:8080  
Запросы из фронта идут на `/api/...` и проксируются на FastAPI.

### Отдельно запустить только backend (без compose)
```bash
cd backend
docker build -t sales-backend .
docker run --rm -p 8000:8000 sales-backend
```

### Отдельно запустить только frontend (без compose)
```bash
cd frontend
docker build -t sales-frontend .
docker run --rm -p 8080:80 sales-frontend
```
