from datetime import datetime, timedelta
from typing import Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, or_

from app.database.database import get_db
from app.database.models import Event, User
from app.dependencies import TEMPLATES_PATH


templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


<<<<<<< Updated upstream
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
=======
#inner class of the router, for the jinja page to process the json
class Event:
    GRID_BAR_QUARTER = 1
    FULL_GRID_BAR = 4
    MIN_MINUTS = 0
    MAX_MINUTS = 15
    BASE_GRID_BAR = 5

    def __init__(self, id: int, color: str, content: str, start_datetime: str, end_datetime: str) -> None:
        self.id = id
        self.color = color
        self.content = content
        self.start_time = datetime.strptime(start_datetime, "%d/%m/%Y %H:%M")
        self.end_time = datetime.strptime(end_datetime, "%d/%m/%Y %H:%M")
        self._set_total_time()
        self._set_grid_position()

    def _minutes_position(self, minutes: int) -> int:
        for i in range(self.GRID_BAR_QUARTER, self.FULL_GRID_BAR + 1):
            if self.MIN_MINUTS <= minutes < self.MAX_MINUTS:
                return i
            self.MIN_MINUTS = self.MAX_MINUTS
            self.MAX_MINUTS += 15

    def _get_position(self, time: datetime) -> int:
        return time.hour * self.FULL_GRID_BAR + self._minutes_position(time.minute) + self.BASE_GRID_BAR
>>>>>>> Stashed changes

    def _get_time_format(self) -> str:
        for multiday in [self.start_multiday, self.end_multiday]:
            yield self.MULTIDAY_FORMAT if multiday else self.DEFAULT_FORMAT

    def _set_total_time(self) -> None:
        length = self.end_time - self.start_time
        self.length = length.seconds / 60
<<<<<<< Updated upstream
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


@router.get('/day/{date}')
#async def dayview(request: Request, date: str, db_session=Depends(get_db), view='day'):
async def dayview(request: Request, date: str, view='day'):
    # TODO: add a login session
    #user = db_session.query(User).filter_by(username='test1').first()
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
        print(day)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=f"{err}")
    day_end = day + timedelta(hours=24)
    '''events = db_session.query(Event).filter(
        Event.owner_id == user.id).filter(
            or_(and_(Event.start >= day, Event.start < day_end),
                and_(Event.end >= day, Event.end < day_end),
                and_(Event.start < day_end, day_end < Event.end)))'''
    start = datetime(year=2021, month=2, day=1, hour=13, minute=13)
    end = datetime(year=2021, month=2, day=1, hour=15, minute=46)
    events = [Event(title='test2', content='test',
                 start=start, end=end, owner_id=1, color='pink')]
    events_n_attrs = [(event, DivAttributes(event, day)) for event in events]
=======
        self.total_time = self.start_time.strftime("%H:%M") + ' - ' + self.end_time.strftime("%H:%M")


@router.post("/dayview")
async def dayview(request: Request):
    form = await request.json()
    events = [Event(**event) for event in form['events']]
>>>>>>> Stashed changes
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events_n_attrs,
        "month": day.strftime("%B").upper(),
        "day": day.day,
        "view": view
        })
