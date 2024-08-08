from telegram import (Update,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup)
from telegram.ext import (Application,
                          ConversationHandler,
                          MessageHandler,
                          CommandHandler,
                          ContextTypes,
                          InlineQueryHandler,
                          CallbackQueryHandler,
                          filters)

import logging

from hid_vars import token

# logging.basicConfig(
#     format="time: %(act_time)s, name: %(name)s, level: %(levelname)s, message: %(message)s",
#     level=logging.INFO
# )
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

LEVELS = zip(("MAIN_MENU", "SCHEDULE", "DAY"), map(chr, range(0, 3)))
# STATES_HIERARCHY = {
#     "MAIN_MENU": {
#         {"SCHEDULE": {
#
#         }},
#         {"SETTINGS": {
#
#         }},
#         {"ABOUT": {
#
#         }}},
# }
# states names
(SELECTING_IN_MAIN_MENU,
 TO_SCHEDULE, SELECTING_IN_SCHEDULE,
 TO_SETTINGS, SELECTING_IN_SETTINGS,
 TO_ABOUT, SELECTING_IN_ABOUT,
 STOP_ALL) = map(chr, range(8))
END = ConversationHandler.END


def get_main_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Расписание", callback_data=TO_SCHEDULE),
            InlineKeyboardButton(text="Настройки", callback_data=TO_SETTINGS)
        ],
        [
            InlineKeyboardButton(text="О проекте", callback_data=TO_ABOUT)
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


def get_back_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Назад", callback_data=END),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    start_text = "Привет, я бот-распределитель задач!"
    await update.message.reply_text(text=start_text)

    text = "Выберите пункт меню:"
    await update.message.reply_text(text=text, reply_markup=get_main_menu_keyboard())

    return SELECTING_IN_MAIN_MENU


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "До встречи!"
    await update.message.reply_text(text=text)

    return STOP_ALL


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Выберите пункт меню:"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=get_main_menu_keyboard())
    return SELECTING_IN_MAIN_MENU


async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Затычка, расписание ещё не сделано"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=get_back_keyboard())
    return SELECTING_IN_SCHEDULE


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Затычка, настройки ещё не сделаны"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=get_back_keyboard())
    return SELECTING_IN_SETTINGS


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "chpdd$$$$$$$$$$$$$$$"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=get_back_keyboard())
    return SELECTING_IN_ABOUT


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

    return END


def main() -> None:
    application = Application.builder().token(token).build()

    schedule_menu_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=f"^{TO_SCHEDULE}$", callback=show_schedule),
        ],
        states={

        },
        fallbacks=[
            CommandHandler(command="stop", callback=stop),
            CallbackQueryHandler(pattern=f"^{END}$", callback=back_to_main_menu),
        ],
        map_to_parent={
            STOP_ALL: STOP_ALL,
            END: SELECTING_IN_MAIN_MENU
        }
    )

    settings_menu_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=f"^{TO_SETTINGS}$", callback=show_settings)
        ],
        states={
            SELECTING_IN_SETTINGS: [

            ]
        },
        fallbacks=[
            CommandHandler(command="stop", callback=stop),
            CallbackQueryHandler(pattern=f"^{END}$", callback=back_to_main_menu)
        ],
        map_to_parent={
            STOP_ALL: STOP_ALL,
            END: SELECTING_IN_MAIN_MENU
        }
    )

    about_menu_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=f"^{TO_ABOUT}$", callback=show_about)
        ],
        states={
            SELECTING_IN_ABOUT: [

            ]
        },
        fallbacks=[
            CommandHandler(command="stop", callback=stop),
            CallbackQueryHandler(pattern=f"^{END}$", callback=back_to_main_menu)
        ],
        map_to_parent={
            STOP_ALL: STOP_ALL,
            END: SELECTING_IN_MAIN_MENU
        }
    )

    main_menu_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            SELECTING_IN_MAIN_MENU: [
                schedule_menu_conv_handler,
                settings_menu_conv_handler,
                about_menu_conv_handler
            ],
        },
        fallbacks=[
            CallbackQueryHandler(pattern=f"^{END}$", callback=stop),
            CommandHandler("stop", stop)
        ],
    )

    application.add_handler(main_menu_conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
