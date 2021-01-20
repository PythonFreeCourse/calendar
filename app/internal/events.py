from operator import attrgetter
from typing import List

from app.database.models import Event


def sort_by_date(events: List[Event]) -> List[Event]:
    """Sorts the events by the start of the event."""

    temp = events.copy()
    temp.sort(key=attrgetter('start'))
    return temp
