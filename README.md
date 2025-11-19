# Telepipe Monorepo

Телепайп — это монорепозиторий из трёх модулей:

```
telepipe/
├── bot/        # Telegram-бот на aiogram 3
├── backend/    # FastAPI сервис загрузки и выдачи видео
├── frontend/   # Next.js фронтенд с видеоплеером
└── storage/    # Локальное хранилище файлов
```

## Запуск

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Bot
```bash
cd bot
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Переменные окружения настраиваются через `.env` файлы внутри каждого модуля
(см. `*.env.example`).
