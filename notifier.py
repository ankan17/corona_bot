import telegram
import datetime
from telegram.error import NetworkError, Unauthorized
from decouple import config


def send_notification(message):
    bot = telegram.Bot(config('BOT_TOKEN'))
    try:
        bot.send_message(config('GROUP_ID'), message)
    except (NetworkError, Unauthorized) as e:
        with open('log.txt', 'a') as f:
            f.write(f"\n{datetime.datetime.now()}:\n{e}\n")


if __name__ == "__main__":
    send_notification(None)
