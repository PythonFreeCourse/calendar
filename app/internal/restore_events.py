from datetime import datetime, timedelta

from typing import List

from app.database.models import Event, UserEvent
from app.dependencies import Session


def delete_events_after_optionals_num_days(days: int, session: Session):
    """
    Delete events permanently after 30 days

    Args:
        days: number of days to delete from
        session: db session
    Returns:
        None
    """
    date_to_delete = datetime.now() - timedelta(days=days)

    user_events_ids_to_be_deleted = (
        session.query(UserEvent)
        .join(Event)
        .filter(Event.deleted_date < date_to_delete)
        .all()
    )

    for id_to_be_deleted in user_events_ids_to_be_deleted:
        (
            session.query(UserEvent)
            .filter(UserEvent.id == id_to_be_deleted.id)
            .delete()
        )

    session.query(Event).filter(Event.deleted_date < date_to_delete).delete()
    session.commit()


def get_event_ids(events_data: List) -> List[str]:
    """
    Get the event ids that need to be restored

    Args:
        events_data: List df events

    Returns:
        Events id
    """
    ids = []
    check_name = "check"
    check_on_value = "on"

    is_checkbox_on = False
    for element, element_value in events_data:
        if is_checkbox_on:
            ids.append(element_value)
            is_checkbox_on = False
        if element == check_name and element_value == check_on_value:
            is_checkbox_on = True
    return ids
