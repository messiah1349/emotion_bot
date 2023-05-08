from telegram import ReplyKeyboardMarkup
import lib.utils as ut

menu_names = ut.get_menu_names()

start_keyboard_options = [
        [menu_names.add_emotion],
        [menu_names.show_last_emotions]
    ]

def get_start_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(start_keyboard_options, one_time_keyboard=False, resize_keyboard=True)
    return markup
