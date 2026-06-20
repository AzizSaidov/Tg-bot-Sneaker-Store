from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
