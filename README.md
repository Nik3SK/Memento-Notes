# Memento Notes

Memento Notes is a lightweight local notes app built with Python.

Проект использует:

- FastAPI для API-слоя
- Streamlit для локального веб-интерфейса
- pytest для тестов
- uv для управления окружением и зависимостями

## Установка

Создайте виртуальное окружение и установите зависимости:

```bash
uv venv
uv pip install -r requirements.txt
```

Создайте локальный файл конфигурации:

```bash
cp .env.example .env
```

Файл `.env` не попадает в git. В репозитории хранится только `.env.example`.

Доступные настройки:

- `MEMENTO_APP_NAME` - название API
- `MEMENTO_APP_VERSION` - версия приложения
- `MEMENTO_LOG_LEVEL` - уровень логирования
- `MEMENTO_STORAGE_DIR` - директория для локального JSON-хранилища заметок

## Запуск API

```bash
uv run uvicorn app.main:app --reload
```

Проверка работоспособности:

```bash
curl http://127.0.0.1:8000/health
```

Версия приложения:

```bash
curl http://127.0.0.1:8000/version
```

Основные маршруты заметок:

- `POST /notes` - создать заметку
- `GET /notes` - получить список заметок
- `GET /notes/{note_id}` - получить заметку
- `PUT /notes/{note_id}` - обновить заметку
- `DELETE /notes/{note_id}` - удалить заметку

## Запуск UI

```bash
uv run streamlit run ui/main.py
```

## Тесты

```bash
uv run pytest
```
