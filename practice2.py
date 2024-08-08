from telegram import InlineKeyboardButton, Update
from telegram.ext import Application, ContextTypes, CommandHandler

import logging


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = "Привет, да, привет. У меня есть команда /caps"
    await update.message.reply_text(text=text)

    return


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.message.text
    await update.message.reply_text(text=text.upper())

    return

async def caps2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return

def main():
    from hid_vars import token

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler(command="start", callback=start))
    application.add_handler(CommandHandler(command="caps", callback=caps2))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
