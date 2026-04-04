# 📦 Telegram Media Comments Downloader

### Скрипт для скачивания медиафайлов (фото, видео) из комментариев к постам в Telegram.

---

## ⚙️ Настройка перед запуском

Файл `.env.example` нужно переименоввать в `.env`.  

Все настройки задаются в файле `.env`.

Содержимое `.env`:

```env
API_ID=123456
API_HASH=abcdef123456

USE_PROXY=true
PROXY_SCHEME=http
PROXY_HOST=123.456.789.123
PROXY_PORT=8000
PROXY_USER=qwerty
PROXY_PASS=qwerty123

DIALOG_TARGET="Chat_name"
```
---

### 🔑 Получение API_ID и API_HASH

1. Перейдите на сайт: https://my.telegram.org/
2. Войдите в аккаунт Telegram (через номер телефона)
3. Выберите раздел **API development tools**
4. Создайте приложение:
   - App title: любое название
   - Short name: любое короткое имя
   - Description: любое описание, несколько предложений
5. После создания будут доступны:
   - `API_ID`
   - `API_HASH`

Скопируйте их в `.env`.

---

### 🌐 Настройка прокси

Если вам нужен прокси:

```env
USE_PROXY=false
PROXY_SCHEME=http      # или socks5
PROXY_HOST=IP_АДРЕС
PROXY_PORT=ПОРТ
PROXY_USER=логин       # если есть
PROXY_PASS=пароль      # если есть
```

- `USE_PROXY=true` → использовать прокси
- `USE_PROXY=false` → прокси не используется

---

### 💬 Выбор чата

```env
DIALOG_TARGET="Chat_name"
```

- Указывается **название чата**, из которого нужно скачать медиафайлы
- Должно точно совпадать как в Telegram

---

## 🐳 Запуск

### 1. Сборка контейнера

```bash
docker compose build
```

### 2. Запуск

```bash
docker compose run --rm tg_comments_archive
```

---

## 📁 Результат

После выполнения появится папка `downloads/`, в которой будут скачанные медифайлы.

---

## ⚠️ Первый запуск

При первом запуске:

- Telegram попросит авторизацию
- Будет создан файл:

```
account.session
```

📌 Не удаляйте его — он используется для повторных запусков без авторизации.
