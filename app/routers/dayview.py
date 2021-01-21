from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, or_

from app.database.database import get_db
from app.database.models import Event, User
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

    def __init__(self, event: Event, day: Optional[datetime] = False) -> None:
        self.start_time = event.start
        self.end_time = event.end
        self.day = day
        self._check_if_multiday_event()
        self.color = self._check_color(event.color)
        self._set_total_time()
        self._set_grid_position()

    def _check_color(self, color: str) -> str:
        if color is None:
            return 'grey'
        else:
            return color

    def _minutes_position(self, minutes: int) -> int:
        for i in range(self.GRID_BAR_QUARTER, self.FULL_GRID_BAR + 1):
            if self.MIN_MINUTES < minutes <= self.MAX_MINUTES:
                return i
            self.MIN_MINUTES = self.MAX_MINUTES
            self.MAX_MINUTES += 15

    def _get_position(self, time: datetime) -> int:
        grid_hour_position = time.hour * self.FULL_GRID_BAR
        grid_minutes_modifier = self._minutes_position(time.minute)
        if grid_minutes_modifier is None:
            grid_minutes_modifier = 0
        return grid_hour_position + grid_minutes_modifier + self.BASE_GRID_BAR

    def _set_grid_position(self) -> None:
        if self.start_multiday:
            start = self.FIRST_GRID_BAR
        else:
            start = self._get_position(self.start_time)
        if self.end_multiday:
            end = self.LAST_GRID_BAR
        else:
            end = self._get_position(self.end_time)
        self.grid_position = f'{start} / {end}'

    def _get_time_format(self):
        format = "%H:%M"
        multiday_format = "%d/%m %H:%M"
        for multiday in [self.start_multiday, self.end_multiday]:
            if multiday:
                yield multiday_format
            else:
                yield format

    def _set_total_time(self) -> None:
        length = self.end_time - self.start_time
        self.length = length.seconds / 60
        format_gen = self._get_time_format()
        start_time_str = self.start_time.strftime(next(format_gen))
        end_time_str = self.end_time.strftime(next(format_gen))
        self.total_time = ' '.join([start_time_str, '-', end_time_str])

    def _check_if_multiday_event(self) -> None:
        self.start_multiday, self.end_multiday = False, False
        if self.day:
            if self.start_time < self.day:
                self.start_multiday = True
            self.day += timedelta(hours=24)
            if self.day <= self.end_time:
                self.end_multiday = True


@router.get('/day/{date}')
async def dayview(request: Request, date: str, db_session=Depends(get_db)):

    # temporary fake user until there will be login session
    user = db_session.query(User).filter_by(username='test1').first()
    day = datetime.strptime(date, '%d-%m-%Y')
    events = db_session.query(Event).filter(
        Event.owner_id == user.id).filter(
            or_(Event.start >= day,
                Event.end < day,
                and_(Event.start < day, day < Event.end)))
    events_n_divAttr = [(event, DivAttributes(event, day)) for event in events]
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events_n_divAttr,
        "MONTH": day.strftime("%B").upper(),
        "DAY": day.day
        })
