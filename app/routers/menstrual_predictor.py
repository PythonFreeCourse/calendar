import datetime
from typing import List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from app.database.models import Event
from app.dependencies import get_db, templates
from app.routers.share import accept
from app.routers.event import create_event
from app.routers.user import create_user

from loguru import logger


# templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/menstrual_predictor",
    tags=["menstrual_predictor"],
    dependencies=[Depends(get_db)]
)

MENSTRUAL_PERIOD_CATEGORY_ID = 111

@router.get("/")
def join(request: Request, db: Session = Depends(get_db)):
    logger.info('getting menstrual predictor')
    return templates.TemplateResponse("join_menstrual_predictor.html", {
        "request": request,
        # TODO:
        # "invitations": get_all_invitations(session=db),
    })


@router.post("/")
async def submit_join_form(
    request: Request,
    db: Session = Depends(get_db)
):
    # user = create_user(username='shimi', password='lalala', email='shimi@shimi.com', language_id=0, session=db, language='hebrew')
    # event = create_event(db, 'period day', datetime.datetime.now(), datetime.datetime.now(), 1, category_id=MENSTRUAL_PERIOD_CATEGORY_ID)
    # db.add(event)
    # db.commit()
    data = await request.form()
    # invite_id = list(data.values())[0]

    # invitation = get_invitation_by_id(invite_id, session=db)
    # accept(invitation, db)

    # url = router.url_path_for("view_invitations")
    url = '/'
    generate_predicted_period_dates(db, 5, datetime.datetime.now(), 1)
    period_days = get_all_period_days(db, user_id=1)
    logger.error(period_days)
    logger.warning(data)
    remove_existing_period_dates(db, user_id=1)
    period_days = get_all_period_days(db, user_id=1)
    for day in period_days:
        logger.error(day.start)

    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


def remove_existing_period_dates(db, user_id):
    period_days = (db.query(Event).
        filter(Event.owner_id == user_id).
        filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID).
        all())
    db.delete(period_days)
    db.commit()


def generate_predicted_period_dates(db, period_length, last_period_time, user_id):
    for i in range(period_length):
        delta = datetime.timedelta(i + 1)
        period_date = last_period_time + delta
        event = create_event(db, 'period day', period_date, period_date, user_id, category_id=MENSTRUAL_PERIOD_CATEGORY_ID)
        db.add(event)
    db.commit()


def get_all_period_days(session: Session, user_id: int) -> List[Event]:
    """Returns all period days filter by user id."""

    try:
        # return [email[0] for email in db.query(User.email).
        #         select_from(Event).
        #         join(UserEvent, UserEvent.event_id == Event.id).
        #         join(User, User.id == UserEvent.user_id).
        #         filter(Event.id == event_id).
        #         all()]
        period_days = list(session.query(Event).
        filter(Event.owner_id == user_id).
        filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID).
        all())

    except SQLAlchemyError as err:
        logger.debug(err)
        return []
    else:
        return period_days


# def get_invitation_by_id(
#         invitation_id: int, session: Session
# ) -> Union[Invitation, None]:
#     """Returns a invitation by an id.
#     if id does not exist, returns None."""

#     return session.query(Invitation).filter_by(id=invitation_id).first()
