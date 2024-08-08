import random

from telegram import Update
from telegram.ext import ContextTypes, Application, ConversationHandler, CommandHandler, MessageHandler, filters

import logging

TYPING_NAME, TYPING_AGE, TYPING_NUMBER, END_OF_SURVEY = map(chr, range(4))


async def start_and_ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Привет, ответь на несколько вопросов:")
    await update.message.reply_text("Как тебя зовут?")

    return TYPING_NAME


async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Сколько тебе лет?")

    return TYPING_AGE


async def ask_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Выбери число от 1 до 9?")

    return TYPING_NUMBER


async def say_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    mes_text: str = update.message.text
    if mes_text.isdigit() and 1 <= int(mes_text) <= 9:
        rand_number = random.randint(1, 9)
        text: str = f"Ты не угадал. Ответ: {rand_number}. КОГДА-НИБУДЬ МОЖЕТ ПОВЕЗЁТ."
        if update.message == rand_number:
            text = "Поздравляю, ты угадал!"
        await update.message.reply_text(text)

        return END_OF_SURVEY

    await update.message.reply_text("Неправильный формат. Укажи ЧИСЛО ОТ 1 ДО 9")

    return TYPING_NUMBER


async def repeat_in_the_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Это конечно всё хорошо, но опрос окончен.")

    return END_OF_SURVEY


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> ConversationHandler.END:
    await update.message.reply_text("Наконец-то. Пока!")

    return ConversationHandler.END


def main() -> None:
    from hid_vars import token

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    script_logger = logging.getLogger(__name__)

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(command="start", callback=start_and_ask_name)
        ],
        states={
            TYPING_NAME: [
                MessageHandler(filters=~filters.COMMAND & filters.TEXT, callback=ask_age)
            ],
            TYPING_AGE: [
                MessageHandler(filters=~filters.COMMAND & filters.TEXT, callback=ask_number)
            ],
            TYPING_NUMBER: [
                MessageHandler(filters=~filters.COMMAND & filters.TEXT, callback=say_result)
            ],
            END_OF_SURVEY: [
                MessageHandler(filters=~filters.COMMAND & filters.TEXT, callback=repeat_in_the_end)
            ]
        },
        fallbacks=[
            CommandHandler(command="stop", callback=stop)
        ]
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
