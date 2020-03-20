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
            updated = False
            tot_old, fr_old, rec_old, died_old = match["total_cases"], \
                match["foreign_nationals"], match["recovered"], match["died"]
            if tot_old != tot:
                match["total_cases"] = tot
                updated = True
            if fr_old != fr:
                match["foreign_nationals"] = fr
                updated = True
            if rec_old != rec:
                match["recovered"] = rec
                updated = True
            if died_old != died:
                match["died"] = died
                updated = True
            if updated:
                updations.append({
                    "name": state,
                    "from": [tot_old, fr_old, rec_old, died_old],
                    "to": [tot, fr, rec, died]
                })
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
                "to": [tot, fr, rec, died]
            })

    message = []
    for data in updations:
        message.append(f"Data for {data['name']} updated: [{' '.join(data['from'])}] -> [{' '.join(data['to'])}]")  # noqa
    for data in insertions:
        message.append(f"New data for {data['name']} added: [{' '.join(data['to'])}]")  # noqa

    if message:
        message = '\n'.join(message)
        with open(os.path.join(dir, 'log.txt'), 'a') as f:
            f.write(f"\n{datetime.datetime.now()}:\n{message}\n")
        send_notification(message)
except Exception as e:
    with open(os.path.join(dir, 'log.txt'), 'a') as f:
        f.write(f"\n{datetime.datetime.now()}:\n{e}\n")
