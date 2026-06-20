import os

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Order
from app.database.requests import (
    add_product,
    delete_product,
    get_all_orders,
    get_all_products,
    get_categories,
    get_or_create_user,
    get_order,
    set_order_status,
)
from app.keyboards import (
    add_category_keyboard,
    admin_menu,
    admin_order_keyboard,
    admin_orders_keyboard,
    delete_products_keyboard,
)
from app.states import AddProduct
from app.texts import status_label, t
from config import settings

router = Router()
router.message.filter(F.from_user.id.in_(settings.admin_ids))
router.callback_query.filter(F.from_user.id.in_(settings.admin_ids))


async def _lang(session: AsyncSession, source: Message | CallbackQuery) -> str:
    user, _ = await get_or_create_user(
        session, source.from_user.id, source.from_user.username, source.from_user.full_name
    )
    return user.lang


def order_detail(order: Order, lang: str) -> str:
    items = "\n".join(
        f"  • {item.product.name} ×{item.quantity} — ${item.price}" for item in order.items
    )
    return (
        f"🧾 <b>Order #{order.id}</b> · {status_label(order.status, lang)}\n\n"
        f"👤 {order.full_name}\n📞 {order.phone}\n🏠 {order.address}\n\n"
        f"{items}\n\n💰 <b>${order.total}</b>"
    )


@router.message(Command("admin"))
async def admin_panel(message: Message, session: AsyncSession) -> None:
    lang = await _lang(session, message)
    await message.answer(t("admin_title", lang), reply_markup=admin_menu(lang))


@router.message(Command("cancel"))
async def admin_cancel(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    lang = await _lang(session, message)
    await state.clear()
    await message.answer(t("admin_title", lang), reply_markup=admin_menu(lang))


@router.callback_query(F.data == "admin:home")
async def admin_home(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    await callback.message.edit_text(t("admin_title", lang), reply_markup=admin_menu(lang))
    await callback.answer()


@router.callback_query(F.data == "admin:orders")
async def admin_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    orders = await get_all_orders(session)
    if not orders:
        await callback.answer(t("admin_no_orders", lang), show_alert=True)
        return
    await callback.message.edit_text(
        t("admin_orders", lang), reply_markup=admin_orders_keyboard(orders, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("aorder:"))
async def admin_open_order(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    order_id = int(callback.data.split(":")[1])
    order = await get_order(session, order_id)
    if order is None:
        await callback.answer()
        return
    await callback.message.edit_text(
        order_detail(order, lang), reply_markup=admin_order_keyboard(order.id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("astatus:"))
async def admin_set_status(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    _, order_id, status = callback.data.split(":")
    await set_order_status(session, int(order_id), status)
    order = await get_order(session, int(order_id))
    await callback.message.edit_text(
        order_detail(order, lang), reply_markup=admin_order_keyboard(order.id, lang)
    )
    await callback.answer(t("status_changed", lang))


@router.callback_query(F.data == "admin:add")
async def add_start(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, callback)
    categories = await get_categories(session)
    await state.set_state(AddProduct.category)
    await callback.message.edit_text(
        t("add_choose_category", lang), reply_markup=add_category_keyboard(categories, lang)
    )
    await callback.answer()


@router.callback_query(AddProduct.category, F.data.startswith("addcat:"))
async def add_category(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, callback)
    await state.update_data(category_id=int(callback.data.split(":")[1]))
    await state.set_state(AddProduct.name)
    await callback.message.edit_text(t("add_name", lang))
    await callback.answer()


@router.message(AddProduct.name)
async def add_name(message: Message, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, message)
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.brand)
    await message.answer(t("add_brand", lang))


@router.message(AddProduct.brand)
async def add_brand(message: Message, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, message)
    await state.update_data(brand=message.text)
    await state.set_state(AddProduct.price)
    await message.answer(t("add_price", lang))


@router.message(AddProduct.price)
async def add_price(message: Message, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, message)
    try:
        price = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer(t("invalid_price", lang))
        return
    await state.update_data(price=price)
    await state.set_state(AddProduct.photo)
    await message.answer(t("add_photo", lang))


@router.message(AddProduct.photo, F.photo)
async def add_photo(message: Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    lang = await _lang(session, message)
    photo = message.photo[-1]
    filename = f"product_{photo.file_unique_id}.jpg"
    await bot.download(photo, destination=os.path.join("media", filename))
    await state.update_data(photo=filename)
    await state.set_state(AddProduct.description)
    await message.answer(t("add_description", lang))


@router.message(AddProduct.photo)
async def add_photo_skip(message: Message, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, message)
    await state.update_data(photo="")
    await state.set_state(AddProduct.description)
    await message.answer(t("add_description", lang))


@router.message(AddProduct.description)
async def add_description(message: Message, session: AsyncSession, state: FSMContext) -> None:
    lang = await _lang(session, message)
    data = await state.get_data()
    await add_product(
        session,
        data["category_id"],
        data["name"],
        data["brand"],
        data["price"],
        data["photo"],
        message.text,
    )
    await state.clear()
    await message.answer(t("product_added", lang), reply_markup=admin_menu(lang))


@router.callback_query(F.data == "admin:del")
async def delete_start(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    products = await get_all_products(session)
    if not products:
        await callback.answer(t("admin_no_products", lang), show_alert=True)
        return
    await callback.message.edit_text(
        t("delete_choose", lang), reply_markup=delete_products_keyboard(products, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delprod:"))
async def delete_product_cb(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    product_id = int(callback.data.split(":")[1])
    await delete_product(session, product_id)
    products = await get_all_products(session)
    if not products:
        await callback.message.edit_text(t("admin_title", lang), reply_markup=admin_menu(lang))
    else:
        await callback.message.edit_text(
            t("delete_choose", lang), reply_markup=delete_products_keyboard(products, lang)
        )
    await callback.answer(t("product_deleted", lang))


@router.callback_query(F.data == "admin:stats")
async def admin_soon(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    await callback.answer(t("soon", lang), show_alert=True)
