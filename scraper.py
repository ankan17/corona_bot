import requests
import os
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from notifier import send_notification
from logger import logger


dir = os.path.dirname(os.path.realpath(__file__))
db = TinyDB(os.path.join(dir, 'database.json'))

try:
    html_doc = requests.get("https://www.mohfw.gov.in/").text
    soup = BeautifulSoup(html_doc, 'html.parser')
    rows = soup.find_all('tr')[1:-1]
except Exception as e:
    logger.error(e)  # Error in accessing the webpage


updations, insertions = [], []
try:
    for row in rows:
        info = [x.get_text().strip() for x in row.find_all('td')]
        if len(info) == 6:
            _, state, tot, fr, rec, died = info

            State = Query()
            matches = db.search(State.name == state)
            if matches:
                match = matches[0]
                updated, obj = False, {"name": state}
                tot_old, fr_old, rec_old, died_old = \
                    match["total_cases"], match["foreign_nationals"], \
                    match["recovered"], match["died"]
                if tot_old != tot:
                    match["total_cases"] = tot
                    updated = True
                    obj["tot_old"] = tot_old
                    obj["tot_new"] = tot
                if fr_old != fr:
                    match["foreign_nationals"] = fr
                    updated = True
                    obj["fr_old"] = fr_old
                    obj["fr_new"] = fr
                if rec_old != rec:
                    match["recovered"] = rec
                    updated = True
                    obj["rec_old"] = rec_old
                    obj["rec_new"] = rec
                if died_old != died:
                    match["died"] = died
                    updated = True
                    obj["died_old"] = died_old
                    obj["died_new"] = died
                if updated:
                    updations.append(obj)
                    db.update(match, State.name == state)
            else:
                db.insert({
                    "name": state,
                    "total_cases": tot,
                    "foreign_nationals": fr,
                    "recovered": rec,
                    "died": died
                })
                insertions.append({
                    "name": state,
                    "tot": tot,
                    "fr": fr,
                    "rec": rec,
                    "died": died
                })

    message = []
    for data in updations:
        if "tot_old" in data:
            message.append(
                "- Total number of case(s) in %s changed from %s to %s" %
                (data['name'], data['tot_old'], data['tot_new'])
            )
        if "fr_old" in data:
            message.append(
                "- Number of foreign foreign national(s) affected in %s changed from %s to %s" %  # noqa
                (data['name'], data['fr_old'], data['fr_new'])
            )
        if "rec_old" in data:
            message.append(
                "- %d patient(s) recovered in %s" %
                (int(data['rec_old'])-int(data['rec_new'])), data['state']
            )
        if "died_old" in data:
            message.append(
                "- %d patient(s) died in %s" %
                (int(data['died_old'])-int(data['died_new'])), data['state']
            )
    for data in insertions:
        new_message = "- New data for %s added: " % (data['name'])
        cases = []
        if int(data['tot']) > 0:
            cases.append("%s total case(s)" % (data['tot']))
        if int(data['fr']) > 0:
            cases.append("%s case(s) of foreign nationals" % (data['fr']))
        if int(data['rec']) > 0:
            cases.append("%s patients recovered" % (data['rec']))
        if int(data['died']) > 0:
            cases.append("%s patients died" % (data['died']))
        new_message += ', '.join(cases)
        message.append(new_message)

    if message:
        message = '\n'.join(message)
        logger.info("\n" + message)
        print(message)
        send_notification(message)
    else:
        logger.info("No new updates")
except Exception as e:
    logger.error(e)  # Error in parsing
