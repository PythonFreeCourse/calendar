from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import models
from app.dependencies import get_db, templates
from app.internal import daily_quotes
from app.internal.security.dependencies import current_user

router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/save")
async def save_quote(
    user: models.User = Depends(current_user),
    quote_id: int = Form(...),
    db: Session = Depends(get_db),
) -> None:
    """Saves a quote in the database."""
    db.merge(models.UserQuotes(user_id=user.user_id, quote_id=quote_id))
    db.commit()


@router.delete("/delete")
async def delete_quote(
    user: models.User = Depends(current_user),
    quote_id: int = Form(...),
    db: Session = Depends(get_db),
) -> None:
    """Deletes a quote from the database."""
    db.query(models.UserQuotes).filter(
        models.UserQuotes.user_id == user.user_id,
        models.UserQuotes.quote_id == quote_id,
    ).delete()
    db.commit()


@router.get("/favorites")
async def favorite_quotes(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
) -> templates.TemplateResponse:
    """html page for displaying the users' favorite quotes."""
    quotes = daily_quotes.get_quotes(db, user.user_id)
    return templates.TemplateResponse(
        "favorite_quotes.html",
        {
            "request": request,
            "quotes": quotes,
        },
    )
