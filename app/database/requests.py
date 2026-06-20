from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import CartItem, Category, Order, OrderItem, Product, User


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


async def add_to_cart(session: AsyncSession, user_id: int, product_id: int) -> None:
    item = await session.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    if item is None:
        session.add(CartItem(user_id=user_id, product_id=product_id, quantity=1))
    else:
        item.quantity += 1
    await session.commit()


async def get_cart_items(session: AsyncSession, user_id: int) -> list[CartItem]:
    result = await session.scalars(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .order_by(CartItem.id)
        .options(selectinload(CartItem.product))
    )
    return list(result)


async def change_cart_quantity(
    session: AsyncSession, user_id: int, product_id: int, delta: int
) -> None:
    item = await session.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    if item is None:
        return
    item.quantity += delta
    if item.quantity <= 0:
        await session.delete(item)
    await session.commit()


async def remove_cart_item(session: AsyncSession, user_id: int, product_id: int) -> None:
    item = await session.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    )
    if item is not None:
        await session.delete(item)
        await session.commit()


async def clear_cart(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await session.commit()


async def create_order(
    session: AsyncSession, user_id: int, full_name: str, phone: str, address: str
) -> Order | None:
    items = await get_cart_items(session, user_id)
    if not items:
        return None
    total = sum(item.product.price * item.quantity for item in items)
    order = Order(
        user_id=user_id, full_name=full_name, phone=phone, address=address, total=total
    )
    session.add(order)
    await session.flush()
    for item in items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )
        )
    await session.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await session.commit()
    return order


async def get_user_orders(session: AsyncSession, user_id: int) -> list[Order]:
    result = await session.scalars(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    return list(result)


async def get_all_orders(session: AsyncSession) -> list[Order]:
    result = await session.scalars(
        select(Order)
        .order_by(Order.id.desc())
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    return list(result)


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    return await session.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )


async def set_order_status(session: AsyncSession, order_id: int, status: str) -> None:
    order = await session.get(Order, order_id)
    if order is not None:
        order.status = status
        await session.commit()


async def add_product(
    session: AsyncSession,
    category_id: int,
    name: str,
    brand: str,
    price: float,
    photo: str,
    description: str,
) -> None:
    session.add(
        Product(
            category_id=category_id,
            name=name,
            brand=brand,
            price=price,
            photo=photo,
            description=description,
            stock=10,
            rating=5.0,
        )
    )
    await session.commit()


async def get_all_products(session: AsyncSession) -> list[Product]:
    result = await session.scalars(select(Product).order_by(Product.id))
    return list(result)


async def delete_product(session: AsyncSession, product_id: int) -> None:
    product = await session.get(Product, product_id)
    if product is not None:
        await session.delete(product)
        await session.commit()
