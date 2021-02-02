from datetime import datetime, timedelta
from typing import Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, or_

from app.database.database import get_db
from app.database.models import Event, User
from app.routers.user import get_all_user_events, create_user
from app.routers.event import create_event
from app.dependencies import TEMPLATES_PATH


templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


class DivAttributes:
    GRID_BAR_QUARTER = 1
    FULL_GRID_BAR = 4
    MIN_MINUTES = 0
    MAX_MINUTES = 15
    BASE_GRID_BAR = 5
    FIRST_GRID_BAR = 1
    LAST_GRID_BAR = 101
    DEFAULT_COLOR = 'grey'
    DEFAULT_FORMAT = "%H:%M"
    MULTIDAY_FORMAT = "%d/%m %H:%M"

    def __init__(self, event: Event,
                 day: Union[bool, datetime] = False) -> None:
        self.start_time = event.start
        self.end_time = event.end
        self.day = day
        self.start_multiday, self.end_multiday = self._check_multiday_event()
        self.color = self._check_color(event.color)
        self.total_time = self._set_total_time()
        self.grid_position = self._set_grid_position()

    def _check_color(self, color: str) -> str:
        if color is None:
            return self.DEFAULT_COLOR
        return color

    def _minutes_position(self, minutes: int) -> Union[int, None]:
        min_minutes = self.MIN_MINUTES
        max_minutes = self.MAX_MINUTES
        for i in range(self.GRID_BAR_QUARTER, self.FULL_GRID_BAR + 1):
            if min_minutes < minutes <= max_minutes:
                return i
            min_minutes = max_minutes
            max_minutes += 15

    def _get_position(self, time: datetime) -> int:
        grid_hour_position = time.hour * self.FULL_GRID_BAR
        grid_minutes_modifier = self._minutes_position(time.minute)
        if grid_minutes_modifier is None:
            grid_minutes_modifier = 0
        return grid_hour_position + grid_minutes_modifier + self.BASE_GRID_BAR

    def _set_grid_position(self) -> str:
        if self.start_multiday:
            start = self.FIRST_GRID_BAR
        else:
            start = self._get_position(self.start_time)
        if self.end_multiday:
            end = self.LAST_GRID_BAR
        else:
            end = self._get_position(self.end_time)
        return f'{start} / {end}'

    def _get_time_format(self) -> str:
        for multiday in [self.start_multiday, self.end_multiday]:
            yield self.MULTIDAY_FORMAT if multiday else self.DEFAULT_FORMAT

    def _set_total_time(self) -> None:
        length = self.end_time - self.start_time
        self.length = length.seconds / 60
        format_gen = self._get_time_format()
        start_time_str = self.start_time.strftime(next(format_gen))
        end_time_str = self.end_time.strftime(next(format_gen))
        return ' '.join([start_time_str, '-', end_time_str])

    def _check_multiday_event(self) -> Tuple[bool]:
        start_multiday, end_multiday = False, False
        if self.day:
            if self.start_time < self.day:
                start_multiday = True
            self.day += timedelta(hours=24)
            if self.day <= self.end_time:
                end_multiday = True
        return (start_multiday, end_multiday)


def get_events_and_attributes(day: datetime, session, user_id: int):
    events = get_all_user_events(session, user_id)
    day_end = day + timedelta(hours=24)
    daily_events = []
    for event in events:
        if ((event.start >= day and event.start < day_end) or
           (event.end >= day and event.end < day_end) or
           (event.start < day_end and day_end < event.end)):
            daily_events.append(event)
    return [(event, DivAttributes(event, day)) for event in daily_events]


@router.get('/day/{date}')
async def dayview(request: Request, date: str, db_session=Depends(get_db), view='day'):
    # TODO: add a login session
    user = db_session.query(User).filter_by(username='test1').first()
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError as err:
        raise HTTPException(status_code=404, detail=f"{err}")
    events_n_attrs = get_events_and_attributes(day=day, session=db_session, user_id=user.id)
    month = day.strftime("%B").upper()
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events_n_attrs,
        "month": month,
        "day": day.day,
        "view": view
        })

@router.get('/create-testuser')
async def create_test_user(request: Request, db_session=Depends(get_db)):
    start = datetime(year=2021, month=3, day=6, hour=5, minute=15)
    end = datetime(year=2021, month=3, day=7, hour=6, minute=45)
    create_event(db=db_session, title='test2', start=start, end=end, owner_id=1)