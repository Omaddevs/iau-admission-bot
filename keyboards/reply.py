from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from utils.texts import TEXTS

def phone_keyboard(lang="uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]["phone_keyboard_text"], request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def remove_keyboard():
    return ReplyKeyboardRemove()
