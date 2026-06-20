import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeChat

from app.database.engine import init_db
from app.handlers import admin, user
from app.middlewares.db import DbSessionMiddleware
from config import settings

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(admin.router)
    dp.include_router(user.router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Restart"),
            BotCommand(command="menu", description="Menu"),
        ]
    )
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Перезапустить"),
            BotCommand(command="menu", description="Меню"),
        ],
        language_code="ru",
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.set_my_commands(
                [
                    BotCommand(command="start", description="Restart"),
                    BotCommand(command="menu", description="Menu"),
                    BotCommand(command="admin", description="Admin panel"),
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception:
            pass

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())