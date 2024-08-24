from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def subscriptions_keyboard():
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="Добавить подписку", callback_data="add_subscription"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить подписку", callback_data="delete_subscription"
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    return keyboard


def reply_keyboard():
    inline_kb_list = [
        [KeyboardButton(text="Мои подписки"), KeyboardButton(text="/start")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=inline_kb_list, resize_keyboard=True)
    return keyboard
