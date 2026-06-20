DEFAULT_LANG = "en"

TEXTS = {
    "en": {
        "choose_language": "🌐 Please choose your language:",
        "language_set": "✅ Language set to English",
        "start": "👟 <b>SneakerShop</b>\n\nWelcome! The sneaker store is opening soon.",
    },
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "language_set": "✅ Язык переключён на русский",
        "start": "👟 <b>SneakerShop</b>\n\nДобро пожаловать! Магазин кроссовок скоро откроется.",
    },
}


def t(key: str, lang: str) -> str:
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, key)
