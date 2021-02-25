from datetime import datetime

from fastapi import APIRouter, Depends, Form, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import templates
from app.dependencies import get_db
from app.internal.todo_list import by_id, create_task
from app.internal.utils import get_current_user

router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/delete")
def delete_task(
        task_id: int = Form(...),
        db: Session = Depends(get_db),
) -> RedirectResponse:
    user = get_current_user(db)
    task = by_id(db, task_id)
    if task.owner_id != user.id:
        return templates.TemplateResponse(
            "calendar_day_view.html",
            {"task_id": task_id},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    date_str = task.date.strftime('%Y-%m-%d')
    try:
        # Delete task
        db.delete(task)

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "calendar_day_view.html",
            {"task_id": task_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return RedirectResponse(
        url=f"/day/{date_str}",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/add")
async def add_task(
        title: str = Form(...),
        description: str = Form(...),
        date_str: str = Form(...),
        time_str: str = Form(...),
        is_important: bool = Form(False),
        session: Session = Depends(get_db),
) -> RedirectResponse:
    user = get_current_user(session)
    create_task(
        session,
        title,
        description,
        datetime.strptime(date_str, '%Y-%m-%d').date(),
        datetime.strptime(time_str, '%H:%M').time(),
        user.id,
        is_important,
    )
    return RedirectResponse(
        f"/day/{date_str}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/edit")
async def edit_task(
        task_id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        date_str: str = Form(...),
        time_str: str = Form(...),
        is_important: bool = Form(False),
        session: Session = Depends(get_db),
) -> RedirectResponse:
    task = by_id(session, task_id)
    task.title = title
    task.description = description
    task.date = datetime.strptime(date_str, '%Y-%m-%d').date()
    task.time = datetime.strptime(time_str, '%H:%M:%S').time()
    task.is_important = is_important
    session.commit()
    return RedirectResponse(
        f"/day/{date_str}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/done/{task_id}")
async def set_task_done(
        task_id: int,
        session: Session = Depends(get_db),
) -> RedirectResponse:
    task = by_id(session, task_id)
    task.is_done = True
    session.commit()
    return RedirectResponse(
        f"/day/{task.date.strftime('%Y-%m-%d')}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/undone/{task_id}")
async def set_task_undone(
        task_id: int,
        session: Session = Depends(get_db),
) -> RedirectResponse:
    task = by_id(session, task_id)
    task.is_done = False
    session.commit()
    return RedirectResponse(
        f"/day/{task.date.strftime('%Y-%m-%d')}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{task_id}")
async def get_task(
        task_id: int,
        session: Session = Depends(get_db),
) -> JSONResponse:
    task = by_id(session, task_id)
    data = jsonable_encoder(task)
    return JSONResponse(content=data)
