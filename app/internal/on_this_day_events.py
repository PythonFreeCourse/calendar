import json
from datetime import datetime

import requests


def get_on_this_day_events():
    now = datetime.now()
    day, month = now.day, now.month

    res = requests.get(
        f'https://byabbe.se/on-this-day/{month}/{day}/events.json')
    events = json.loads(res.text)

    return events
