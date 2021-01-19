import os
from datetime import datetime
from typing import Optional, Set, Tuple, Union

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database.models import Event
from app.database.database import get_db

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)

def check_validation(start_time, end_time):
    """Check if the start_date is smaller then the end_time"""
    if start_time < end_time:
        return True
    return False


def get_event_by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""
    event = db.query(Event).filter(Event.id == event_id).first()
    return event


def prepre_mail_for_update_event(old_event: Event, new_event: Event, link_to_event: str) -> Tuple[str]:
    """prepre text for the email thet will send on update event"""
    title = old_event.title + ' updated'
    body = ''
    if old_event.title != new_event.title:
        body += 'title changed - from: ' + old_event.title + ' to: ' + new_event.title
        body += '\n'
    if old_event.location != new_event.location:
        if old_event.location:
            body += 'location changed - from: ' + \
                old_event.location + ' to: ' + new_event.location
        else:
            body += 'location added ' + new_event.location
        body += '\n'
    if old_event.start_date != new_event.start_date or old_event.end_date != new_event.end_date:
        body += 'the evant time has changed - from: ' + str(old_event.start_date) + ' - ' + str(
            old_event.end_date) + '/nto: ' + str(new_event.start_date) + ' - ' + str(new_event.end_date)
        body += '\n'
    if old_event.VC_link != new_event.VC_link:
        if old_event.VC_link:
            body += 'link changed - from: ' + old_event.VC_link + ' to: ' + new_event.VC_link
        else:
            body += 'link added ' + new_event.VC_link
        body += '\n'
    if old_event.content != new_event.content:
        if old_event.content:
            body += 'content changed - from: ' + \
                old_event.content + ' to: ' + new_event.content
        else:
            body += 'content added ' + new_event.content
        body += '\n'
    body += 'Link to updated event: ' + link_to_event
    # להוסיף שורה ולבקש לאשר מחדש
    return (title, body)


@router.post('/{event_id}/edit')
def update_event(request: Request,
                 event_id: int,
                 event_title: str = Form(...),
                 location: Optional[str] = Form(None),
                 from_date: Optional[datetime] = Form(...),
                 to_date: Optional[datetime] = Form(...),
                 content: str = Form(None),
                 link_vc: str = Form(None),
                 repeated_event: str = Form(None),
                 db: Session = Depends(get_db)
                 ) -> Set[Union[str, int]]:
    # To DO: לבדוק שהמשתמש הוא יוצר האירוע
            #  אם לא זהה, להחזיר שגיאה
    success = False
    error_msg = ""
    if not check_validation(from_date, to_date):
        error_msg = "Error, Your date is invalid"
        return {success, event_id, error_msg}
    old_event = get_event_by_id(db=db, event_id=event_id)
    if old_event is None:
        error_msg = "Error, An event does not exist"
        return {success, event_id, error_msg}
    props = {'title': event_title, 'location': location,
             'start_date': from_date, 'end_date': to_date, 'content': content,
             'VC_link': link_vc}
    update_event = Event(id=event_id, owner_id=old_event.owner_id, **props)
    # לבדוק מי הנמענים ואם ישנם
    link_to_event = os.path.dirname(str(request.url))
    # יצירת מייל לעדכונים:
    title, body = prepre_mail_for_update_event(
        old_event, update_event, link_to_event)
    print(title, body)
    # לבדוק פונקצית שליחה
    if 'from' not in body:
        error_msg = "Error, No changes"
        return {success, event_id, error_msg}
    try:
        db.query(Event).filter(Event.id).update(
            props, synchronize_session=False)
        db.commit()
        success = True
        # שליחת המיילים ואיפוס אישורי הגעה
    except AttributeError:
        error_msg = "Error occurred"
    print(event_id)
    return {success, event_id, error_msg}
print(datetime.now())