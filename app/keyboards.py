from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import Category, Product
from app.texts import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            ]
        ]
    )


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_catalog", lang), callback_data="menu:catalog")],
            [
                InlineKeyboardButton(text=t("btn_cart", lang), callback_data="menu:cart"),
                InlineKeyboardButton(text=t("btn_orders", lang), callback_data="menu:orders"),
            ],
            [InlineKeyboardButton(text=t("btn_ai", lang), callback_data="menu:ai")],
            [InlineKeyboardButton(text=t("btn_language", lang), callback_data="menu:language")],
        ]
    )


def categories_keyboard(categories: list[Category], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{c.emoji} {c.name}", callback_data=f"cat:{c.id}")]
        for c in categories
    ]
    rows.append([InlineKeyboardButton(text=t("btn_menu", lang), callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_keyboard(
    category_id: int, index: int, total: int, product_id: int, lang: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️", callback_data=f"pg:{category_id}:{index - 1}"),
                InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton(text="▶️", callback_data=f"pg:{category_id}:{index + 1}"),
            ],
            [InlineKeyboardButton(text=t("btn_add_cart", lang), callback_data=f"add:{product_id}")],
            [
                InlineKeyboardButton(text=t("btn_categories", lang), callback_data="menu:catalog"),
                InlineKeyboardButton(text=t("btn_menu", lang), callback_data="menu:home"),
            ],
        ]
    )
