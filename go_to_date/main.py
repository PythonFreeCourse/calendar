from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates/")

@app.get("/")
async def hellow_world():
    return "{'key': 'value'}"

@app.get("/go_to", response_class=HTMLResponse)
async def go_to(request: Request):
    return templates.TemplateResponse("go_to_date.html", {"request": request})
