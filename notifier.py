import telegram
from decouple import config
from logger import logger


def send_notification(message):
    bot = telegram.Bot(config('BOT_TOKEN'))
    try:
        bot.send_message(config('GROUP_ID'), message)
        logger.info("Message sent successfully")
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    send_notification(None)
