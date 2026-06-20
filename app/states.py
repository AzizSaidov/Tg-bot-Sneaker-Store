from aiogram.fsm.state import State, StatesGroup


class Checkout(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    confirm = State()
