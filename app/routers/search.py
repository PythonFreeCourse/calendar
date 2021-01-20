from app.database.database import get_db
from app.dependencies import templates
from app.internal.search import get_results_by_keywords
from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/search")
def search(request: Request):
    current_username = "Chuck Norris"
    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": current_username
    })


@router.post("/search")
async def show_results(request: Request, keywords: str = Form(None), db: Session = Depends(get_db)):
    current_username = "Chuck Norris"
    current_user = 1
    
    message = ""

    if not keywords:
        message = "Invalid request."
        results = None
    else:
        results = get_results_by_keywords(db, keywords, owner_id=current_user)
        if len(results) == 0:
            message = f"No matching results for '{keywords}'."
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": current_username,
        "message": message,
        "results": results,
        "keywords": keywords
    })
