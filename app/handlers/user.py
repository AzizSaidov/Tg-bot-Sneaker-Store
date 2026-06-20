from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.requests import get_or_create_user, set_user_lang
from app.keyboards import language_keyboard, main_menu
from app.texts import t

router = Router()


async def _user(session: AsyncSession, source: Message | CallbackQuery):
    return await get_or_create_user(
        session,
        source.from_user.id,
        source.from_user.username,
        source.from_user.full_name,
    )


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


@router.callback_query(F.data.startswith("menu:"))
async def menu_placeholder(callback: CallbackQuery, session: AsyncSession) -> None:
    user, _ = await _user(session, callback)
    await callback.answer(t("soon", user.lang), show_alert=True)
