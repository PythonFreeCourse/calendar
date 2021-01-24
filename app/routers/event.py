from app.database.models import Event

def check_validation(start_time, end_time) -> bool:
    """Check if the start_date is smaller then the end_time"""
    try:
        return start_time < end_time
    except TypeError:
        return False



def add_event(values: dict, db) -> Event:
    """Get User values and the DB Session insert the values to the DB and refresh it
    exception in case that the keys in the dict is not match to the fields in the DB
    return the Event Class item"""
    try:
        new_event = Event(**values)
        db.add(new_event)   
        db.commit()
        db.refresh(new_event)
        return new_event
    except (AssertionError, AttributeError) as e:
        # Need to write into log
        print(e)
        return None
