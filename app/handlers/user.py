from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.requests import get_or_create_user, set_user_lang
from app.keyboards import language_keyboard
from app.texts import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    user, created = await get_or_create_user(
        session,
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )
    if created:
        await message.answer(
            t("choose_language", user.lang), reply_markup=language_keyboard()
        )
    else:
        await message.answer(t("start", user.lang))


@router.message(Command("language"))
async def cmd_language(message: Message, session: AsyncSession) -> None:
    user, _ = await get_or_create_user(
        session,
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )
    await message.answer(
        t("choose_language", user.lang), reply_markup=language_keyboard()
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = callback.data.split(":")[1]
    user, _ = await get_or_create_user(
        session,
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name,
    )
    await set_user_lang(session, user, lang)
    await callback.message.edit_text(t("start", lang))
    await callback.answer(t("language_set", lang))
