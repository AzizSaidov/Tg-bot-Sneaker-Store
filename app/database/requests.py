from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Category, Product, User


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


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.scalars(select(Category).order_by(Category.id))
    return list(result)


async def get_products(session: AsyncSession, category_id: int) -> list[Product]:
    result = await session.scalars(
        select(Product).where(Product.category_id == category_id).order_by(Product.id)
    )
    return list(result)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.scalar(select(Product).where(Product.id == product_id))
