from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db, templates
from app.internal.search import get_results_by_keywords

router = APIRouter()


@router.get("/search")
def search(request: Request):
    # Made up user details until there's a user login system
    current_username = "Chuck Norris"

    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": current_username
    })


@router.post("/search")
async def show_results(
        request: Request,
        keywords: str = Form(None),
        db: Session = Depends(get_db)):
    # Made up user details until there's a user login system
    current_username = "Chuck Norris"
    current_user = 1

    message = ""

    if not keywords:
        message = "Invalid request."
        results = None
    else:
        results = get_results_by_keywords(db, keywords, owner_id=current_user)
        if not results:
            message = f"No matching results for '{keywords}'."

    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": current_username,
        "message": message,
        "results": results,
        "keywords": keywords
    }
    )
