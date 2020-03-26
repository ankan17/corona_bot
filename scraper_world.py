import requests
import os
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from notifier import send_notification
from logger import logger


dir = os.path.dirname(os.path.realpath(__file__))
db = TinyDB(os.path.join(dir, 'world_database.json'))

try:
    html_doc = requests.get("https://www.worldometers.info/coronavirus/").text
    soup = BeautifulSoup(html_doc, 'html.parser')
    rows = soup.find_all('tr')[1:-1]
except Exception as e:
    logger.error(e)  # Error in accessing the webpage


updations, insertions = [], []
try:
    for row in rows:
        info = [x.get_text().strip().replace(',', '') for x in row.find_all('td')]
        info = [x if x else '0' for x in info]
        if len(info) > 0:
            country, total, death, recovered, active, serious = \
                info[0], int(info[1]), int(info[3]), int(info[5]), int(info[6]), int(info[7])

            Country = Query()
            matches = db.search(Country.name == country)
            if matches:
                match = matches[0]
                updated, obj = False, {"name": country}
                death_old, rec_old, serious_old = \
                    match["death"], match["recovered"], match["serious"]
                if match["total"] != total:
                    match["total"] = total
                    updated = True
                    obj["total"] = total
                if match["active"] != active:
                    match["active"] = active
                    updated = True
                    obj["active"] = active
                if rec_old != recovered:
                    match["recovered"] = recovered
                    updated = True
                    obj["rec_old"] = rec_old
                    obj["rec_new"] = recovered
                if death_old != death:
                    match["death"] = death
                    updated = True
                    obj["death_old"] = death_old
                    obj["death_new"] = death
                if serious_old != serious:
                    match["serious"] = serious
                    updated = True
                    obj["serious_old"] = serious_old
                    obj["serious_new"] = serious
                if updated:
                    updations.append(obj)
                    db.update(match, Country.name == country)
            else:
                db.insert({
                    "name": country,
                    "total": total,
                    "death": death,
                    "recovered": recovered,
                    "active": active,
                    "serious": serious
                })
                insertions.append({
                    "name": country,
                    "total": total,
                    "death": death,
                    "recovered": recovered,
                    "active": active,
                    "serious": serious
                })

    message = []
    for data in updations:
        if "total" in data:
            message.append(
                "- Total cases in %s has increased to %s" %
                (data['name'], data['total'])
            )
        if "active" in data:
            message.append(
                "- Total active cases in %s has increased to %s" %
                (data['name'], data['active'])
            )
        if "death_old" in data:
            message.append(
                "- Total death toll in %s has risen from %s to %s" %
                (data['name'], data['death_old'], data['death_new'])
            )
        if "serious_old" in data:
            message.append(
                "- Total serious cases in %s has risen from %s to %s" %
                (data['name'], data['serious_old'], data['serious_new'])
            )
        if "rec_old" in data:
            message.append(
                "- Total number of recovered patients in %s has risen from %s to %s" %
                (data['name'], data['rec_old'], data['rec_new'])
            )
    for data in insertions:
        new_message = "- New data for %s added: " % (data['name'])
        cases = []
        if data['total'] > 0:
            cases.append("%d total cases" % (data['total']))
        if data['active'] > 0:
            cases.append("%d active cases" % (data['active']))
        if data['serious'] > 0:
            cases.append("%d serious cases" % (data['serious']))
        if data['recovered'] > 0:
            cases.append("%d patients recovered" % (data['recovered']))
        if data['death'] > 0:
            cases.append("%d patients died" % (data['death']))
        new_message += ', '.join(cases)
        message.append(new_message)

    if message:
        message = '\n'.join(message)
        logger.info("\n" + message)
        print(message)
        send_notification(message)
    else:
        logger.info("No new updates from the world")
except Exception as e:
    logger.error(e)  # Error in parsing
