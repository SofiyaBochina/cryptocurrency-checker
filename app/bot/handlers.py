import functools
import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from database.queries import (
    add_subscription,
    delete_subscription,
    get_subscription,
    get_user_subscriptions,
)
from settings.logger import logger

from .keyboards import reply_keyboard, subscriptions_keyboard
from .states import AddSubscription, DeleteSubscription

router = Router()

logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiogram").handlers = logger.handlers

reply_kb = reply_keyboard()
sub_kb = subscriptions_keyboard()


def with_logger(handler):
    @functools.wraps(handler)
    async def wrapper(*args, **kwargs):
        mes = args[0]
        state = kwargs.get("state")
        user_id = mes.from_user.id
        username = mes.from_user.username
        text, data = None, None
        if isinstance(mes, CallbackQuery):
            text = mes.message.text
            data = mes.data
        elif isinstance(mes, Message):
            text = mes.text
        current_state = await state.get_state()
        logger.info(
            f"Handler: {handler.__name__} - User: {user_id}, username: {username}, "
            f"message: '{text}', data: {data}, state: {current_state}"
        )
        return await handler(*args, **kwargs)

    return wrapper


@router.message(Command(commands=["start", "help"]))
@with_logger
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Этот бот предназначен для отслеживания курсов криптовалют и "
        "отправки уведомлений при достижении порогов (минимального и максимального).\n"
        "Вы можете подписаться на интересующую вас валюту путём добавления новой подписки и указания параметров. "
        "Если хотите отписаться - удалите нужную подписку после указания её ID.\n"
        'Для старта перейдите в раздел "Мои подписки".',
        reply_markup=reply_kb,
    )


@router.message(F.text == "Мои подписки")
@with_logger
async def show_subscriptions(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    subscriptions = get_user_subscriptions(user_id)
    response = "Ваши подписки:\n"
    if subscriptions:
        for row in subscriptions:
            response += f"ID: {row.id}, символ: {row.symbol}, мин. порог: {row.min_threshold}, макс. порог: {row.max_threshold}\n"
    else:
        response += "Подписок пока что нет"
    await message.answer(response, reply_markup=sub_kb)


@router.callback_query(F.data == "add_subscription")
@with_logger
async def process_add_subscription(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddSubscription.waiting_for_symbol.state)
    await call.message.answer(
        "Введите символ криптовалюты для новой подписки (например BTC):",
        reply_markup=reply_kb,
    )


@router.message(StateFilter(AddSubscription.waiting_for_symbol))
@with_logger
async def process_symbol(message: Message, state: FSMContext):
    symbol = message.text.upper()
    if symbol.isascii():
        await state.update_data(symbol=symbol)
        await state.set_state(AddSubscription.waiting_for_min_currency.state)
        await message.reply(
            "Введите значение минимального порога (например 5.0):",
            reply_markup=reply_kb,
        )
    else:
        await message.reply(
            "Вы ввели значение неправильного формата, попробуйте ещё раз",
            reply_markup=reply_kb,
        )


@router.message(StateFilter(AddSubscription.waiting_for_min_currency))
@with_logger
async def process_min_currency(message: Message, state: FSMContext):
    min_threshold = None
    try:
        min_threshold = float(message.text)
    except:
        await message.reply(
            "Вы ввели значение неправильного формата, попробуйте ещё раз",
            reply_markup=reply_kb,
        )
    if min_threshold:
        await state.update_data(min_threshold=min_threshold)
        await state.set_state(AddSubscription.waiting_for_max_currency.state)
        await message.reply(
            "Введите значение минимального порога (например 10.0):",
            reply_markup=reply_kb,
        )


@router.message(StateFilter(AddSubscription.waiting_for_max_currency))
@with_logger
async def process_max_currency(message: Message, state: FSMContext):
    max_threshold = None
    try:
        max_threshold = float(message.text)
    except:
        await message.reply(
            "Вы ввели значение неправильного формата, попробуйте ещё раз",
            reply_markup=reply_kb,
        )
    if max_threshold:
        user_id = message.from_user.id
        state_data = await state.get_data()
        if add_subscription(
            user_id,
            state_data.get("symbol"),
            state_data.get("min_threshold"),
            max_threshold,
        ):
            await message.reply("Подписка успешно добавлена!", reply_markup=reply_kb)
        else:
            await message.reply("Не удалось добавить подписку.", reply_markup=reply_kb)
        await state.clear()


@router.callback_query(F.data == "delete_subscription")
@with_logger
async def process_delete_subscription(call: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteSubscription.waiting_for_subscription_id.state)
    await call.message.answer(
        "Введите ID подписки для удаления:", reply_markup=reply_kb
    )


@router.message(StateFilter(DeleteSubscription.waiting_for_subscription_id))
@with_logger
async def process_subscription_id(message: Message, state: FSMContext):
    subscription_id = None
    try:
        subscription_id = int(message.text)
    except:
        await message.reply(
            "Вы ввели значение неправильного формата, попробуйте ещё раз",
            reply_markup=reply_kb,
        )
    if subscription_id:
        user_id = message.from_user.id
        subscription = get_subscription(subscription_id)
        if subscription and subscription.user_id == user_id:
            if delete_subscription(subscription_id):
                await message.reply("Подписка успешно удалена!", reply_markup=reply_kb)
            else:
                await message.reply(
                    "Не удалось удалить подписку.", reply_markup=reply_kb
                )
            await state.clear()
        else:
            await message.reply(
                "У вас нет подписки с таким ID, попробуйте ещё раз",
                reply_markup=reply_kb,
            )


@router.message()
@with_logger
async def unknown_command(message: Message, state: FSMContext):
    await message.answer("Неизвестная команда.", reply_markup=reply_kb)
