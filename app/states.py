from aiogram.fsm.state import State, StatesGroup


class Checkout(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    confirm = State()


class AddProduct(StatesGroup):
    category = State()
    name = State()
    brand = State()
    price = State()
    photo = State()
    description = State()


class AiChat(StatesGroup):
    active = State()
