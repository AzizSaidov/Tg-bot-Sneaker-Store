from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Order
from app.database.requests import (
    get_all_orders,
    get_or_create_user,
    get_order,
    set_order_status,
)
from app.keyboards import admin_menu, admin_order_keyboard, admin_orders_keyboard
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


@router.callback_query(F.data.in_({"admin:add", "admin:stats"}))
async def admin_soon(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback)
    await callback.answer(t("soon", lang), show_alert=True)
