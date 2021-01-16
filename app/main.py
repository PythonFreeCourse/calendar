import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
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
    date = datetime.now()
    return templates.TemplateResponse("monthview.html", {
        "request": request,
        "dates": {
            'date': date,
            'month_days': calendar_grid.get_month_days(date.year, date.month),
            'days_of_the_week': calendar_grid.DAYS_OF_THE_WEEK,
            'day': calendar_grid.get_day_name(date),
        }})

if __name__ == "__main__":
    uvicorn.run(app)
