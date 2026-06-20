from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import CartItem, Category, Order, Product
from app.texts import STATUSES, status_label, t


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


def cart_keyboard(items: list[CartItem], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for item in items:
        product = item.product
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{product.name} — ${product.price}×{item.quantity}",
                    callback_data="noop",
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(text="➖", callback_data=f"dec:{product.id}"),
                InlineKeyboardButton(text=str(item.quantity), callback_data="noop"),
                InlineKeyboardButton(text="➕", callback_data=f"inc:{product.id}"),
                InlineKeyboardButton(text="🗑", callback_data=f"del:{product.id}"),
            ]
        )
    rows.append([InlineKeyboardButton(text=t("btn_checkout", lang), callback_data="checkout")])
    rows.append([InlineKeyboardButton(text=t("btn_clear", lang), callback_data="cart:clear")])
    rows.append([InlineKeyboardButton(text=t("btn_menu", lang), callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cart_empty_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_catalog", lang), callback_data="menu:catalog")],
            [InlineKeyboardButton(text=t("btn_menu", lang), callback_data="menu:home")],
        ]
    )


def back_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_menu", lang), callback_data="menu:home")]
        ]
    )


def confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_confirm", lang), callback_data="order:confirm"),
                InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="order:cancel"),
            ]
        ]
    )


def admin_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("admin_orders", lang), callback_data="admin:orders")],
            [InlineKeyboardButton(text=t("admin_add_product", lang), callback_data="admin:add")],
            [InlineKeyboardButton(text=t("admin_delete", lang), callback_data="admin:del")],
            [InlineKeyboardButton(text=t("admin_stats", lang), callback_data="admin:stats")],
        ]
    )


def add_category_keyboard(categories: list[Category], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{c.emoji} {c.name}", callback_data=f"addcat:{c.id}")]
        for c in categories
    ]
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def delete_products_keyboard(products: list[Product], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"🗑 {p.brand} {p.name}", callback_data=f"delprod:{p.id}")]
        for p in products
    ]
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_orders_keyboard(orders: list[Order], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"#{o.id} · {status_label(o.status, lang)} · ${o.total}",
                callback_data=f"aorder:{o.id}",
            )
        ]
        for o in orders
    ]
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_order_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=status_label(s, lang), callback_data=f"astatus:{order_id}:{s}")]
        for s in STATUSES
    ]
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:orders")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
