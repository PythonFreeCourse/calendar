from datetime import datetime, timedelta
from app.database.models import Event, UserEvent


def delete_events_after_optionals_num_days(days, session):
    date_to_delete = datetime.now() - timedelta(days=days)

    user_events_ids_to_be_deleted = session.query(UserEvent).join(Event).filter(
        Event.deleted_date < date_to_delete).all()

    for id_to_be_deleted in user_events_ids_to_be_deleted:
        session.query(UserEvent).filter(UserEvent.id == id_to_be_deleted.id).delete()

    session.query(Event).filter(Event.deleted_date < date_to_delete).delete()
    session.commit()


def get_events_ids_to_restored(events_data):
    ids = []
    check_element_name = 'check'
    check_element_on_value = 'on'

    is_checkbox_element_is_on = False
    for element, element_value in events_data:
        if is_checkbox_element_is_on:
            ids.append(element_value)
            is_checkbox_element_is_on = False
        if element == check_element_name and element_value == check_element_on_value:
            is_checkbox_element_is_on = True
    return ids
