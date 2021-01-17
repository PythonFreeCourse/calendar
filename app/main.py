import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import calendar_grid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/monthview")
async def monthview(request: Request):
    date = datetime.date.today()
    return templates.TemplateResponse("monthview.html", {
        "request": request,
        "calendar": {
            'date': date,
            'strf_date': calendar_grid.get_date_as_string(date),
            'days_of_the_week': calendar_grid.DAYS_OF_THE_WEEK,
            'month_block': calendar_grid.get_month_block(
                datetime.date(date.year, date.month, 1)
            )
        }})


if __name__ == "__main__":
    uvicorn.run(app)
