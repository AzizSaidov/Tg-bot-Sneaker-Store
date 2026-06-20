from groq import AsyncGroq

from config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

SHOP_FACTS = {
    "en": "Delivery: 2-5 business days. Payment: card or cash on delivery. Returns: within 14 days.",
    "ru": "Доставка: 2-5 рабочих дней. Оплата: картой или наличными при получении. Возврат: в течение 14 дней.",
}

SYSTEM = {
    "en": (
        "You are a friendly sales consultant for SneakerShop, an online sneaker store. "
        "Help the customer pick sneakers and answer questions about products, their orders and delivery. "
        "Recommend ONLY sneakers from the catalog below — never invent products, prices or stock. "
        "Do not promise discounts, delivery dates or availability beyond the shop info. "
        "If asked about anything unrelated to sneakers or our shop, politely decline and steer back to shopping. "
        "Keep answers short and helpful. Always reply in English.\n\n"
        "Customer name: {name}\n"
        "Customer orders:\n{orders}\n\n"
        "Catalog:\n{catalog}\n\n"
        "Shop info: {facts}"
    ),
    "ru": (
        "Ты дружелюбный продавец-консультант магазина кроссовок SneakerShop. "
        "Помогай подобрать кроссовки и отвечай на вопросы о товарах, заказах клиента и доставке. "
        "Рекомендуй ТОЛЬКО кроссовки из каталога ниже — никогда не выдумывай товары, цены или наличие. "
        "Не обещай скидки, сроки доставки или наличие сверх информации магазина. "
        "Если спрашивают о чём-то не связанном с кроссовками или магазином — вежливо откажись и верни к покупкам. "
        "Отвечай коротко и по делу. Всегда отвечай на русском.\n\n"
        "Имя клиента: {name}\n"
        "Заказы клиента:\n{orders}\n\n"
        "Каталог:\n{catalog}\n\n"
        "Инфо магазина: {facts}"
    ),
}


async def consult(
    history: list[dict], lang: str, name: str, catalog: str, orders: str
) -> str:
    system = SYSTEM.get(lang, SYSTEM["en"]).format(
        name=name, orders=orders, catalog=catalog, facts=SHOP_FACTS.get(lang, SHOP_FACTS["en"])
    )
    completion = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "system", "content": system}, *history],
        temperature=0.3,
        max_tokens=400,
    )
    return completion.choices[0].message.content
