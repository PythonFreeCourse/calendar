from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile, email


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(email.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"

    })

# test email send
# test insert to db
# build demo to it
# test all security and insert into db


# @app.post("/")
# async def get_clean_text(request: Request):
#     data = await request.form()
#     html = data["editordata"]
#     print(html)
#     allowed_tags = [
#         'a', 'abbr', 'b', 'blockquote', 'br', 'strike', 'u',
#         'code', 'dd', 'del', 'div', 'dl', 'dt', 'em',
#         'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li',
#         'ol', 'p', 'pre', 's', 'strong', 'sub', 'sup',
#         'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul', 'span', 'font'
#     ]
#     allowed_attrs = {
#         '*': ['class', 'style'],
#         'a': ['href', 'rel'],
#         'abbr': ['title'],
#         'style': ['font'],
#         'font': ['color']
#     }
#     allowed_styles = [
#         'color', 'font-weight',
#         'font color', 'background-color',
#         'font', 'font-family', 'font-color'
#     ]
#     html_sanitized = bleach.clean(
#         html,
#         tags=allowed_tags,
#         attributes=allowed_attrs,
#         styles=allowed_styles,
#         strip=True
#     )
#     print(html_sanitized)

#     return templates.TemplateResponse("home.html", {
#         "request": request,
#         "message": html_sanitized,

#     })
