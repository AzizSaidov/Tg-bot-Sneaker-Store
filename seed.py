import asyncio

from app.database.engine import init_db, session_maker
from app.database.models import Category, Product
from app.database.requests import get_categories

CATEGORIES = [
    ("Running", "🏃"),
    ("Lifestyle", "✨"),
    ("Basketball", "🏀"),
]

PRODUCTS = [
    ("Running", "Air Zoom Pegasus 41", "Nike", 129.99, "Responsive everyday running shoe with Air Zoom cushioning.", "nike_pegasus_41.jpg", 25, 4.8),
    ("Running", "Ultraboost Light", "Adidas", 189.99, "Lightweight Boost midsole for an energy-returning ride.", "adidas_ultraboost_light.jpg", 18, 4.7),
    ("Running", "Gel-Nimbus 26", "Asics", 159.99, "Plush long-distance comfort with GEL technology.", "asics_gel_nimbus_26.jpg", 12, 4.6),
    ("Lifestyle", "Air Force 1 '07", "Nike", 119.99, "The timeless classic that never goes out of style.", "nike_air_force_1.jpg", 40, 4.9),
    ("Lifestyle", "Samba OG", "Adidas", 99.99, "Iconic low-profile silhouette with a gum sole.", "adidas_samba_og.jpg", 33, 4.8),
    ("Lifestyle", "550", "New Balance", 129.99, "Retro basketball look reborn as a street staple.", "new_balance_550.jpg", 21, 4.7),
    ("Basketball", "Jordan 1 Retro High", "Nike", 179.99, "Legendary high-top with premium leather.", "jordan_1_retro_high.jpg", 15, 4.9),
    ("Basketball", "LeBron XXI", "Nike", 199.99, "Explosive cushioning built for the modern game.", "nike_lebron_21.jpg", 9, 4.5),
    ("Basketball", "Curry 11", "Under Armour", 159.99, "Lightweight traction for quick guards.", "ua_curry_11.jpg", 14, 4.6),
]


async def main() -> None:
    await init_db()
    async with session_maker() as session:
        if await get_categories(session):
            print("DB already seeded, skipping")
            return

        categories = {}
        for name, emoji in CATEGORIES:
            category = Category(name=name, emoji=emoji)
            session.add(category)
            categories[name] = category
        await session.flush()

        for cat, name, brand, price, description, photo, stock, rating in PRODUCTS:
            session.add(
                Product(
                    category_id=categories[cat].id,
                    name=name,
                    brand=brand,
                    price=price,
                    description=description,
                    photo=photo,
                    stock=stock,
                    rating=rating,
                )
            )
        await session.commit()
        print(f"seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products")


if __name__ == "__main__":
    asyncio.run(main())
