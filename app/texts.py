DEFAULT_LANG = "en"

TEXTS = {
    "en": {
        "choose_language": "🌐 Please choose your language:",
        "language_set": "✅ Language set to English",
        "menu": "👟 <b>SneakerShop</b>\n\nWhat are we looking for today?",
        "btn_catalog": "🛍 Catalog",
        "btn_cart": "🛒 Cart",
        "btn_orders": "🧾 My Orders",
        "btn_ai": "🤖 AI Assistant",
        "btn_language": "🌐 Language",
        "soon": "🚧 Coming soon",
    },
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "language_set": "✅ Язык переключён на русский",
        "menu": "👟 <b>SneakerShop</b>\n\nЧто будем искать сегодня?",
        "btn_catalog": "🛍 Каталог",
        "btn_cart": "🛒 Корзина",
        "btn_orders": "🧾 Мои заказы",
        "btn_ai": "🤖 AI-консультант",
        "btn_language": "🌐 Язык",
        "soon": "🚧 Скоро будет",
    },
}


def t(key: str, lang: str) -> str:
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, key)
