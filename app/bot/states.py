from aiogram.fsm.state import State, StatesGroup


class AddSubscription(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_min_currency = State()
    waiting_for_max_currency = State()


class DeleteSubscription(StatesGroup):
    waiting_for_subscription_id = State()
