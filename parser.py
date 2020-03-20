import requests
import datetime
import os
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from notifier import send_notification


dir = os.path.dirname(os.path.realpath(__file__))
db = TinyDB(os.path.join(dir, 'database.json'))

try:
    html_doc = requests.get("https://www.mohfw.gov.in/").text
    soup = BeautifulSoup(html_doc, 'html.parser')

    updations, insertions = [], []
    rows = soup.find_all('tr')[1:-1]

    for row in rows:
        _, state, tot, fr, rec, died = map(lambda x: x.get_text(), row.find_all('td'))  # noqa

        State = Query()
        matches = db.search(State.name == state)
        if matches:
            match = matches[0]
            updated, obj = False, {"name": state}
            tot_old, fr_old, rec_old, died_old = match["total_cases"], \
                match["foreign_nationals"], match["recovered"], match["died"]
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
            message.append("- Total number of case(s) in %s changed from %s to %s" % (data['name'], data['tot_old'], data['tot_new']))  # noqa
        if "fr_old" in data:
            message.append("- Number of foreign foreign national(s) affected in %s changed from %s to %s" % (data['name'], data['tot_old'], data['tot_new']))  # noqa
        if "rec_old" in data:
            message.append("- %d patient(s) recovered in %s" % (int(data['rec_old'])-int(data['rec_new'])), data['state'])  # noqa
        if "died_old" in data:
            message.append("- %d patient(s) died in %s" % (int(data['rec_old'])-int(data['rec_new'])), data['state'])  # noqa
    for data in insertions:
        message.append("- New data for %s added: %s total case(s), %s case(s) of foreign nationals, %s patients and %s patients died" % (data['name'], data['tot'], data['fr'], data['rec'], data['died']))  # noqa

    if message:
        message = '\n'.join(message)
        with open(os.path.join(dir, 'log.txt'), 'a') as f:
            f.write(f"\n{datetime.datetime.now()}:\n{message}\n")
        send_notification(message)
except Exception as e:
    with open(os.path.join(dir, 'log.txt'), 'a') as f:
        f.write(f"\n{datetime.datetime.now()}:\n{e}\n")
