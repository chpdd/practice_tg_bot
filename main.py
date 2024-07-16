import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters

from hid_vars import token

# Loggers
# for all
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# for httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
# for this file
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def remove_job_by_name(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    jobs_by_name = context.job_queue.get_jobs_by_name(name)
    if not jobs_by_name:
        return False
    for job in jobs_by_name:
        job.schedule_removal()
    return True


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(
        job.chat_id,
        text=f"Message by timer: '{job.data}'"
    )


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    try:
        seconds, alarm_text = float(context.args[0]), str(context.args[1])
        if seconds < 0:
            await update.message.reply_text("Number of seconds less than 0")
            return

        remove_job_flag = remove_job_by_name(str(chat_id), context)
        context.job_queue.run_once(alarm, chat_id=chat_id, when=seconds, data=alarm_text, name=str(chat_id))

        answer_text = "The timer has been successfully set"
        if remove_job_flag:
            answer_text += "(the last timer has been unset)"
        await update.message.reply_text(answer_text)

    except (IndexError, ValueError):
        await update.message.reply_text("Incorrect data, please try again")


async def unset_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if remove_job_by_name(str(chat_id), context):
        await update.message.reply_text("The timer was successfully unset")
    else:
        await update.message.reply_text("No timer")


def main():
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset_timer", unset_timer))
    application.add_handler(MessageHandler(
        filters.TEXT & ~(filters.COMMAND), echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
