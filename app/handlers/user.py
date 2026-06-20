import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product
from app.database.requests import (
    get_categories,
    get_or_create_user,
    get_products,
    set_user_lang,
)
from app.keyboards import (
    categories_keyboard,
    language_keyboard,
    main_menu,
    product_keyboard,
)
from app.texts import t

router = Router()


async def _user(session: AsyncSession, source: Message | CallbackQuery):
    return await get_or_create_user(
        session,
        source.from_user.id,
        source.from_user.username,
        source.from_user.full_name,
    )


def product_caption(product: Product, lang: str) -> str:
    return (
        f"<b>{product.brand} {product.name}</b>\n\n"
        f"⭐ {product.rating}    📦 {t('in_stock', lang)}: {product.stock}\n"
        f"💰 <b>${product.price}</b>\n\n"
        f"{product.description}"
    )


async def show_product(
    message: Message, session: AsyncSession, category_id: int, index: int, lang: str
) -> None:
    products = await get_products(session, category_id)
    if not products:
        await message.answer(t("empty_category", lang))
        return

    index %= len(products)
    product = products[index]
    caption = product_caption(product, lang)
    keyboard = product_keyboard(category_id, index, len(products), product.id, lang)

    photo_path = os.path.join("media", product.photo)
    if product.photo and os.path.exists(photo_path):
        await message.answer_photo(FSInputFile(photo_path), caption=caption, reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    user, created = await _user(session, message)
    if created:
        await message.answer(
            t("choose_language", user.lang), reply_markup=language_keyboard()
        )
    else:
        await message.answer(t("menu", user.lang), reply_markup=main_menu(user.lang))


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession) -> None:
    user, _ = await _user(session, message)
    await message.answer(t("menu", user.lang), reply_markup=main_menu(user.lang))


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = callback.data.split(":")[1]
    user, _ = await _user(session, callback)
    await set_user_lang(session, user, lang)
    await callback.message.edit_text(t("menu", lang), reply_markup=main_menu(lang))
    await callback.answer(t("language_set", lang))


@router.callback_query(F.data == "menu:language")
async def open_language(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await callback.message.edit_text(
        t("choose_language", user.lang), reply_markup=language_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:catalog")
async def open_catalog(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    categories = await get_categories(session)
    await callback.message.delete()
    await callback.message.answer(
        t("catalog_title", user.lang), reply_markup=categories_keyboard(categories, user.lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:home")
async def open_home(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await callback.message.delete()
    await callback.message.answer(t("menu", user.lang), reply_markup=main_menu(user.lang))
    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def menu_placeholder(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await callback.answer(t("soon", user.lang), show_alert=True)


@router.callback_query(F.data.startswith("cat:"))
async def open_category(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    category_id = int(callback.data.split(":")[1])
    await callback.message.delete()
    await show_product(callback.message, session, category_id, 0, user.lang)
    await callback.answer()


@router.callback_query(F.data.startswith("pg:"))
async def page_product(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    _, category_id, index = callback.data.split(":")
    await callback.message.delete()
    await show_product(callback.message, session, int(category_id), int(index), user.lang)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("add:"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await callback.answer(t("soon", user.lang), show_alert=True)
