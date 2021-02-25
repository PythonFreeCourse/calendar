from bisect import bisect_left
from datetime import datetime, timedelta
from typing import Dict, Iterator, Optional, Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Request

from app.database.models import Event, User
from app.dependencies import get_db, templates
from app.internal import international_days, weekly_parasha, zodiac
from app.internal.security.dependencies import current_user

# from app.internal.security.schema import CurrentUser
from app.routers.user import get_all_user_events

router = APIRouter()


class DivAttributes:
    GRID_BAR_QUARTER = 1
    FULL_GRID_BAR = 4
    MIN_MINUTES = 0
    MAX_MINUTES = 15
    BASE_GRID_BAR = 3
    FIRST_GRID_BAR = 1
    LAST_GRID_BAR = 101
    DEFAULT_COLOR = "grey"
    DEFAULT_FORMAT = "%H:%M"
    MULTIDAY_FORMAT = "%d/%m %H:%M"
    CLASS_SIZES = ("title-size-tiny", "title-size-xsmall", "title-size-small")
    LENGTH_SIZE_STEP = (30, 45, 90)

    def _minutes_position(self, minutes: int) -> Dict[str, int]:
        """
        Provides info about the minutes value.
        Returns a Dict that contains-
        'minutes position': calculates the number of grid bar quarters
        that the minutes value covers (from 1 to 4).
        'min_deviation': calculates the 'spare' minutes left out
        of a grid bar quarter.
        (used to indicate the accurate current time)
        """
        min_minutes = self.MIN_MINUTES
        max_minutes = self.MAX_MINUTES
        for i in range(self.GRID_BAR_QUARTER, self.FULL_GRID_BAR + 1):
            if min_minutes < minutes <= max_minutes:
                minute_deviation = minutes - (i - 1) * self.MAX_MINUTES
                return {"min_position": i, "min_deviation": minute_deviation}
            min_minutes = max_minutes
            max_minutes += self.MAX_MINUTES

    def _get_position(self, time: datetime) -> int:
        grid_hour_position = time.hour * self.FULL_GRID_BAR
        grid_minutes_modifier = self._minutes_position(time.minute)
        if grid_minutes_modifier is None:
            grid_minutes_modifier = 0
        else:
            grid_minutes_modifier = grid_minutes_modifier["min_position"]
        return grid_hour_position + grid_minutes_modifier + self.BASE_GRID_BAR


class CurrentTimeAttributes(DivAttributes):
    def __init__(self, date: datetime) -> None:
        current = datetime.now()
        self.dayview_date = date.date()
        self.is_viewed = self._date_is_today()
        self.grid_position = self._get_position(current) - 1
        self.sub_grid_position = self._minutes_position(current.minute)
        self.sub_grid_position = self.sub_grid_position["min_deviation"]

    def _date_is_today(self) -> bool:
        today = datetime.today().date()
        return today == self.dayview_date


class EventsAttributes(DivAttributes):
    def __init__(
        self,
        event: Event,
        day: Union[bool, datetime] = False,
    ) -> None:
        self.start_time = event.start
        self.end_time = event.end
        self.day = day
        self.start_multiday, self.end_multiday = self._check_multiday_event()
        self.color = self._check_color(event.color)
        self.total_time = self._set_total_time()
        self.total_time_visible = self._set_total_time_visiblity()
        self.title_size_class = self._set_title_size()
        self.grid_position = self._set_grid_position()

    def _check_color(self, color: str) -> str:
        if color is None:
            return self.DEFAULT_COLOR
        return color

    def _set_grid_position(self) -> str:
        if self.start_multiday:
            start = self.FIRST_GRID_BAR
        else:
            start = self._get_position(self.start_time)
        if self.end_multiday:
            end = self.LAST_GRID_BAR
        else:
            end = self._get_position(self.end_time)
        return f"{start} / {end}"

    def _get_time_format(self) -> Iterator[str]:
        for multiday in [self.start_multiday, self.end_multiday]:
            yield self.MULTIDAY_FORMAT if multiday else self.DEFAULT_FORMAT

    def _set_total_time(self) -> str:
        length = self.end_time - self.start_time
        self.length = length.seconds / 60
        format_gen = self._get_time_format()
        start_time_str = self.start_time.strftime(next(format_gen))
        end_time_str = self.end_time.strftime(next(format_gen))
        return " ".join([start_time_str, "-", end_time_str])

    def _set_total_time_visiblity(self) -> bool:
        return self.length > 60

    def _set_title_size(self) -> Optional[str]:
        i = bisect_left(self.LENGTH_SIZE_STEP, self.length)
        if i < len(self.CLASS_SIZES):
            return self.CLASS_SIZES[i]

    def _check_multiday_event(self) -> Tuple[bool, bool]:
        start_multiday, end_multiday = False, False
        if self.day:
            if self.start_time < self.day:
                start_multiday = True
            self.day += timedelta(hours=24)
            if self.day <= self.end_time:
                end_multiday = True
        return (start_multiday, end_multiday)


def is_specific_time_event_in_day(
    event: Event,
    day: datetime,
    day_end: datetime,
) -> bool:
    if event.all_day:
        return False
    return bool(
        (event.start >= day and event.start < day_end)
        or (event.end >= day and event.end < day_end)
        or (event.start < day_end < event.end),
    )


def is_all_day_event_in_day(
    event: Event,
    day: datetime,
    day_end: datetime,
) -> bool:
    if not event.all_day:
        return False
    return bool(
        (event.start >= day and event.start < day_end)
        or (event.end >= day and event.end < day_end)
        or (event.start < day_end < event.end),
    )


def get_events_and_attributes(
    day: datetime,
    session,
    user_id: int,
) -> Iterator[Tuple[Event, EventsAttributes]]:
    events = get_all_user_events(session, user_id)
    day_end = day + timedelta(hours=24)
    for event in events:
        if is_specific_time_event_in_day(event, day, day_end):
            yield event, EventsAttributes(event, day)


def get_all_day_events(
    day: datetime,
    session,
    user_id: int,
) -> Iterator[Event]:
    events = get_all_user_events(session, user_id)
    day_end = day + timedelta(hours=24)
    for event in events:
        if is_all_day_event_in_day(event=event, day=day, day_end=day_end):
            yield event


@router.get("/day/{date}", include_in_schema=False)
async def dayview(
    request: Request,
    date: str,
    view="day",
    session=Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as err:
        raise HTTPException(status_code=404, detail=f"{err}")
    zodiac_obj = zodiac.get_zodiac_of_day(session, day)
    parasha_obj = weekly_parasha.get_parasha_object(session, day.date())
    events_with_attrs = get_events_and_attributes(
        day=day,
        session=session,
        user_id=user.user_id,
    )
    all_day_events = get_all_day_events(
        day=day,
        session=session,
        user_id=user.user_id,
    )
    current_time_with_attrs = CurrentTimeAttributes(date=day)
    inter_day = international_days.get_international_day_per_day(session, day)
    month = day.strftime("%B").upper()
    return templates.TemplateResponse(
        "calendar_day_view.html",
        {
            "request": request,
            "events_and_attrs": events_with_attrs,
            "all_day_events": all_day_events,
            "month": month,
            "day": day.day,
            "international_day": inter_day,
            "zodiac": zodiac_obj,
            "view": view,
            "current_time": current_time_with_attrs,
            "parasha": parasha_obj,
        },
    )
