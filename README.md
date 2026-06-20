# 👟 SneakerShop Bot

A full-featured Telegram **e-commerce bot** for a sneaker store, with a built-in **AI sales consultant**, a complete **admin panel**, and **bilingual (EN/RU)** support.

Built with **aiogram 3** and **async SQLAlchemy**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_async-red)

---

## ✨ Features

- 🛍 **Catalog** — categories, product cards with photos, price, rating, stock, and ◀️ ▶️ pagination
- 🛒 **Cart** — add to cart, change quantity (➖ / ➕), remove items, clear cart, live total
- 💳 **Checkout** — step-by-step order form (name → phone → address → confirm) via FSM
- 🧾 **My Orders** — order history with status and items
- 🌐 **Bilingual** — English / Russian with one-tap language switch, saved per user
- 🤖 **AI Consultant (Groq)** — recommends sneakers from the real catalog, knows the customer and their orders, answers stock/delivery questions, and politely declines off-topic requests
- 🛠 **Admin Panel** (`/admin`) — view orders & change status, add / delete products, sales statistics
- 🗄 **Async database** — SQLAlchemy 2.0 + SQLite (aiosqlite)

---

## 🧱 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | language |
| aiogram 3.x | async Telegram framework |
| SQLAlchemy 2.0 (async) | ORM |
| aiosqlite | SQLite driver |
| pydantic-settings | config from `.env` |
| groq | AI consultant (Llama via Groq) |

---

## 📸 Screenshots

| Welcome | Catalog | AI Consultant | Admin |
|---|---|---|---|
| _add screenshot_ | _add screenshot_ | _add screenshot_ | _add screenshot_ |

---

## 📂 Project Structure

```
.
├── main.py                 # entry point: bot startup
├── config.py               # settings from .env
├── seed.py                 # demo data (categories + products)
├── app/
│   ├── database/
│   │   ├── models.py       # tables
│   │   ├── engine.py       # async engine + session + init_db
│   │   └── requests.py     # all DB queries
│   ├── handlers/
│   │   ├── user.py         # customer: catalog, cart, checkout, orders, AI
│   │   └── admin.py        # admin panel
│   ├── keyboards.py        # inline & reply keyboards
│   ├── states.py           # FSM states
│   ├── texts.py            # EN/RU translations
│   ├── ai.py               # Groq client + prompt
│   └── middlewares/
│       └── db.py           # injects a DB session into handlers
└── media/                  # product & welcome images
```

---

## 🚀 Getting Started

### 1. Clone & create a virtual environment
```bash
git clone https://github.com/AzizSaidov/Tg-bot-Sneaker-Store.git
cd Tg-bot-Sneaker-Store
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```
BOT_TOKEN=your_token_from_botfather
ADMIN_IDS=your_telegram_id
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
DB_URL=sqlite+aiosqlite:///shop.db
```
- `BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
- `ADMIN_IDS` — your numeric Telegram ID (from [@userinfobot](https://t.me/userinfobot)); comma-separated for several admins
- `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)

### 4. Seed demo data
```bash
python seed.py
```

### 5. Run the bot
```bash
python main.py
```
Open the bot in Telegram and press **START** (or send `/start`).

> ⚠️ Run only **one** instance at a time — two pollers on the same token cause Telegram conflicts.

---

## 🛠 Admin

Send `/admin` (the bot owner only). From there you can manage orders and their status, add or delete products, and view sales statistics.

---

## 📝 Notes

- Demo product images are placeholders — swap them for your own under the same filenames in `media/`.
- `.env` and `shop.db` are git-ignored.
