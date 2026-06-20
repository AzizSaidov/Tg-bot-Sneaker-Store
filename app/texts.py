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
        "catalog_title": "🛍 <b>Catalog</b>\n\nChoose a category:",
        "in_stock": "In stock",
        "empty_category": "No products in this category yet.",
        "btn_add_cart": "🛒 Add to cart",
        "btn_categories": "⬅️ Categories",
        "btn_menu": "🏠 Menu",
        "cart_title": "🛒 <b>Your Cart</b>",
        "cart_empty": "🛒 Your cart is empty.",
        "cart_total": "Total",
        "added_to_cart": "✅ Added to cart",
        "btn_checkout": "💳 Checkout",
        "btn_clear": "🗑 Clear cart",
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
        "catalog_title": "🛍 <b>Каталог</b>\n\nВыберите категорию:",
        "in_stock": "В наличии",
        "empty_category": "В этой категории пока нет товаров.",
        "btn_add_cart": "🛒 В корзину",
        "btn_categories": "⬅️ Категории",
        "btn_menu": "🏠 Меню",
        "cart_title": "🛒 <b>Ваша корзина</b>",
        "cart_empty": "🛒 Ваша корзина пуста.",
        "cart_total": "Итого",
        "added_to_cart": "✅ Добавлено в корзину",
        "btn_checkout": "💳 Оформить заказ",
        "btn_clear": "🗑 Очистить корзину",
    },
}


def t(key: str, lang: str) -> str:
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, key)
