from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.dependencies import TEMPLATES_PATH


templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


# inner class of the router, for the jinja page to process the json
class Event:
    GRID_BAR_QUARTER = 1
    FULL_GRID_BAR = 4
    MIN_MINUTS = 0
    MAX_MINUTS = 15
    BASE_GRID_BAR = 5

    def __init__(self, id: int, color: str, content: str,
                 start_datetime: str, end_datetime: str) -> None:
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
        grid_hour_position = time.hour * self.FULL_GRID_BAR
        grid_minutes_modifier = self._minutes_position(time.minute)
        return grid_hour_position + grid_minutes_modifier + self.BASE_GRID_BAR

    def _set_grid_position(self) -> None:
        start = self._get_position(self.start_time)
        end = self._get_position(self.end_time)
        self.grid_position = f'{start} / {end}'

    def _set_total_time(self):
        length = self.end_time - self.start_time
        self.length = length.seconds / 60

        start_time_str = self.start_time.strftime("%H:%M")
        end_time_str = self.end_time.strftime("%H:%M")
        self.total_time =  ' '.join([start_time_str, '-', end_time_str])


@router.post("/dayview")
async def dayview(request: Request):
    form = await request.json()
    events = [Event(**event) for event in form['events']]
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events,
        "MONTH": events[0].start_time.strftime("%B").upper(),
        "DAY": form['day']
        })