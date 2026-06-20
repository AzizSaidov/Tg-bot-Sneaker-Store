import os

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product, User
from app.database.requests import (
    add_to_cart,
    change_cart_quantity,
    clear_cart,
    create_order,
    get_cart_items,
    get_categories,
    get_or_create_user,
    get_products,
    get_user_orders,
    remove_cart_item,
    set_user_lang,
)
from app.keyboards import (
    back_menu_keyboard,
    cart_empty_keyboard,
    cart_keyboard,
    categories_keyboard,
    confirm_keyboard,
    language_keyboard,
    main_menu,
    product_keyboard,
)
from app.states import Checkout
from app.texts import status_label, t
from config import settings

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


async def render_cart(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    items = await get_cart_items(session, user.id)
    if not items:
        await callback.message.edit_text(
            t("cart_empty", user.lang), reply_markup=cart_empty_keyboard(user.lang)
        )
        return
    total = sum(item.product.price * item.quantity for item in items)
    text = f"{t('cart_title', user.lang)}\n\n{t('cart_total', user.lang)}: <b>${total}</b>"
    await callback.message.edit_text(text, reply_markup=cart_keyboard(items, user.lang))


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


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    user, _ = await _user(session, message)
    await state.clear()
    await message.answer(t("order_cancelled", user.lang), reply_markup=main_menu(user.lang))


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


@router.callback_query(F.data == "menu:cart")
async def open_cart(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await render_cart(callback, session, user)
    await callback.answer()


@router.callback_query(F.data == "menu:orders")
async def open_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    orders = await get_user_orders(session, user.id)
    if not orders:
        text = t("orders_empty", user.lang)
    else:
        blocks = []
        for order in orders:
            items = "\n".join(
                f"  • {item.product.name} ×{item.quantity}" for item in order.items
            )
            blocks.append(
                f"<b>#{order.id}</b> · {status_label(order.status, user.lang)} · "
                f"<b>${order.total}</b>\n{items}"
            )
        text = t("orders_title", user.lang) + "\n\n" + "\n\n".join(blocks)
    await callback.message.edit_text(text, reply_markup=back_menu_keyboard(user.lang))
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
async def add_product(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    product_id = int(callback.data.split(":")[1])
    await add_to_cart(session, user.id, product_id)
    await callback.answer(t("added_to_cart", user.lang))


@router.callback_query(F.data.startswith("inc:"))
async def inc_item(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    product_id = int(callback.data.split(":")[1])
    await change_cart_quantity(session, user.id, product_id, 1)
    await render_cart(callback, session, user)
    await callback.answer()


@router.callback_query(F.data.startswith("dec:"))
async def dec_item(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    product_id = int(callback.data.split(":")[1])
    await change_cart_quantity(session, user.id, product_id, -1)
    await render_cart(callback, session, user)
    await callback.answer()


@router.callback_query(F.data.startswith("del:"))
async def del_item(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    product_id = int(callback.data.split(":")[1])
    await remove_cart_item(session, user.id, product_id)
    await render_cart(callback, session, user)
    await callback.answer()


@router.callback_query(F.data == "cart:clear")
async def cart_clear(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await clear_cart(session, user.id)
    await render_cart(callback, session, user)
    await callback.answer()


@router.callback_query(F.data == "checkout")
async def checkout_start(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    user, _ = await _user(session, callback)
    items = await get_cart_items(session, user.id)
    if not items:
        await callback.answer(t("cart_empty", user.lang), show_alert=True)
        return
    await state.set_state(Checkout.full_name)
    await callback.message.answer(t("checkout_name", user.lang))
    await callback.answer()


@router.message(Checkout.full_name)
async def checkout_name(message: Message, session: AsyncSession, state: FSMContext) -> None:
    user, _ = await _user(session, message)
    await state.update_data(full_name=message.text)
    await state.set_state(Checkout.phone)
    await message.answer(t("checkout_phone", user.lang))


@router.message(Checkout.phone)
async def checkout_phone(message: Message, session: AsyncSession, state: FSMContext) -> None:
    user, _ = await _user(session, message)
    await state.update_data(phone=message.text)
    await state.set_state(Checkout.address)
    await message.answer(t("checkout_address", user.lang))


@router.message(Checkout.address)
async def checkout_address(message: Message, session: AsyncSession, state: FSMContext) -> None:
    user, _ = await _user(session, message)
    await state.update_data(address=message.text)
    data = await state.get_data()
    items = await get_cart_items(session, user.id)
    total = sum(item.product.price * item.quantity for item in items)
    lines = "\n".join(f"• {item.product.name} ×{item.quantity}" for item in items)
    text = (
        f"{t('checkout_confirm', user.lang)}\n\n"
        f"{lines}\n\n"
        f"{t('cart_total', user.lang)}: <b>${total}</b>\n\n"
        f"👤 {data['full_name']}\n📞 {data['phone']}\n🏠 {data['address']}"
    )
    await state.set_state(Checkout.confirm)
    await message.answer(text, reply_markup=confirm_keyboard(user.lang))


@router.callback_query(Checkout.confirm, F.data == "order:confirm")
async def order_confirm(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot
) -> None:
    user, _ = await _user(session, callback)
    data = await state.get_data()
    order = await create_order(
        session, user.id, data["full_name"], data["phone"], data["address"]
    )
    await state.clear()
    if order is None:
        await callback.message.edit_text(t("cart_empty", user.lang))
        await callback.answer()
        return
    await callback.message.edit_text(t("order_placed", user.lang).format(id=order.id))
    await callback.message.answer(t("menu", user.lang), reply_markup=main_menu(user.lang))
    for admin_id in settings.admin_ids:
        await bot.send_message(
            admin_id,
            f"🔔 <b>New order #{order.id}</b>\n"
            f"👤 {data['full_name']}\n📞 {data['phone']}\n🏠 {data['address']}\n"
            f"💰 <b>${order.total}</b>",
        )
    await callback.answer()


@router.callback_query(Checkout.confirm, F.data == "order:cancel")
async def order_cancel(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    user, _ = await _user(session, callback)
    await state.clear()
    await callback.message.edit_text(t("order_cancelled", user.lang))
    await callback.message.answer(t("menu", user.lang), reply_markup=main_menu(user.lang))
    await callback.answer()
