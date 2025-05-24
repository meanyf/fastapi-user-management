# Yadro 2025

Веб-приложение на FastAPI для работы с данными пользователей.

## 🔧 Установка и запуск

```bash
# Клонируйте репозиторий
git clone https://github.com/meanyf/yadro-2025.git
cd yadro-2025

# Скопируйте пример файла .env и отредактируйте под себя
cp .env.example .env
# Внутри .env укажите:
# - свой пароль пользователя postgres
# - имя вашей базы данных (она создастся автоматически при первом запуске)
# Пример строки подключения:
# DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/yourdbname

# Установите зависимости
python -m pip install -r requirements.txt

# Запустите приложение
python -m uvicorn app.main:app --reload

# Запустите тесты
pytest
