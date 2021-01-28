from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates/")


@app.get('/')
def read_form():
    return 'hello world'


@app.get("/form")
def form_post(request: Request):
    result = "Type a number"
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result})


@app.post("/form")
def form_post(request: Request):
    result = 21
    return templates.TemplateResponse('form.html', {'request': request, 'result': result})