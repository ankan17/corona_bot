# Corona Bot

A Telegram bot that gives latest updates about confirmed COVID-19 cases in India, pulling the information from the website of the Indian Ministry of Health and Family Welfare (https://www.mohfw.gov.in/)

### How to deploy:

1. Create directory: `mkdir corona_bot && cd corona_bot`
2. Clone the repo: `git clone github.com/ankan17/corona_bot.git src`
3. Create a virtual environment: `python3 -m venv .`
4. Activate virtual environment: `source bin/activate`
5. Install dependencies: `pip3 install -r requirements.txt`
6. Use the instructions here to generate the bot token and get the group id: https://dev.to/mddanishyusuf/build-telegram-bot-to-send-daily-notification-4i00
7. Copy the **.env.example** file and update the bot token and the group id: `cp src/.env.example src/.env` and update the .env file
8. Check if **parser.py** is working properly: `python3 parser.py` (You should see a message)
9. Schedule the job using crontab (this schedules the job to run every 10 minutes)
```
env EDITOR=nano crontab -e
*/10 * * * * cd path/to/corona_bot && source bin/activate && python3 src/parser.py >/tmp/stdout.log 2>/tmp/stderr.log
```
10. Done!

Source of information: https://www.mohfw.gov.in/
