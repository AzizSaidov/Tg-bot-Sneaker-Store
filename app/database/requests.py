from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def get_or_create_user(
    session: AsyncSession,
    tg_id: int,
    username: str | None,
    full_name: str | None,
) -> tuple[User, bool]:
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user is not None:
        return user, False
    user = User(tg_id=tg_id, username=username, full_name=full_name)
    session.add(user)
    await session.commit()
    return user, True


async def set_user_lang(session: AsyncSession, user: User, lang: str) -> None:
    user.lang = lang
    await session.commit()
