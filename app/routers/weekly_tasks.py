import calendar
import datetime

from typing import List, Tuple
from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND, HTTP_303_SEE_OTHER

from app.database.models import User, WeeklyTask
from app.dependencies import get_db, templates
from app.internal.weekly_tasks import (
    remove_weekly_task, weekly_task_from_input,
    create_weekly_task, change_weekly_task)


router = APIRouter(
    prefix="/weekly-tasks",
    tags=["weekly-tasks"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_db)]
)


def get_placeholder_user() -> User:
    user = User(
        username='demo_user',
        email='demo@email.po',
        password='s3jsd183b13',
        full_name='The Demo'
    )
    return user


def get_user(
    demo_user: User,
    session: Session = Depends(get_db)
) -> User:
    demo_username = demo_user.username
    user = session.query(User).filter_by(username=demo_username).first()
    if not user:
        session.add(demo_user)
        session.commit()
        user_query = session.query(User)
        user = user_query.filter_by(username=demo_username).first()
    return user


def get_checked_days(days: str = "") -> List[Tuple[str, str, str]]:
    """Produces the input checked_days for the template add_edit_weekly_task"""
    days_list = days.split(", ")
    checked_days = []
    for day_full_name in calendar.day_name:
        day = day_full_name[:3]
        day_lower = day.lower()
        if day in days_list:
            checked_days.append((day_full_name, day_lower, "checked"))
        else:
            checked_days.append((day_full_name, day_lower, ""))
    return checked_days


def get_days_string(
    sun: bool, mon: bool,
    tue: bool, wed: bool,
    thu: bool, fri: bool,
    sat: bool
) -> str:
    """Produces a string of all the days that were checked,
    For use in the model weekly tasks."""
    days_dict = {
        "Mon": mon,
        "Tue": tue,
        "Wed": wed,
        "Thu": thu,
        "Fri": fri,
        "Sat": sat,
        "Sun": sun
    }
    days_list = [day for day, is_checked in days_dict.items() if is_checked]
    days = ", ".join(days_list)
    return days


@router.get('/')
async def weekly_tasks_manager(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_placeholder_user)):

    user = get_user(demo_user, session)

    # TODO: Move the below function to a compatible location
    # Need to run regularly whenever there are tasks on the week
    # Or will run on the background after the user left the
    # weekly-tasks manager page
    # function:
    # generate_tasks(user, session)  # imported from app.internal.weekly_tasks
    # session.close()

    return templates.TemplateResponse("weekly_tasks_manager.html", {
        "request": request,
        "weekly_tasks": user.weekly_tasks
    })


@router.get('/add')
def add_weekly_task(request: Request):

    checked_days = get_checked_days()
    return templates.TemplateResponse("add_edit_weekly_task.html", {
        "request": request,
        "weekly_task": None,
        "mode": "add",
        "checked_days": checked_days
    })


@router.delete('/')
def delete_weekly_task(
        remove_id: int,
        session=Depends(get_db)):

    remove_weekly_task(remove_id, session)
    session.close()
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_303_SEE_OTHER)


@router.post('/edit')
def edit_weekly_task(
        request: Request,
        session=Depends(get_db),
        edit_id: int = Form(...)):

    weekly_task = session.query(WeeklyTask).filter_by(id=edit_id).first()
    checked_days = get_checked_days(weekly_task.days)
    return templates.TemplateResponse("add_edit_weekly_task.html", {
        "request": request,
        "weekly_task": weekly_task,
        "mode": "edit",
        "checked_days": checked_days
    })


@router.post('/execute')
def weekly_task_execute(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_placeholder_user),
        title: str = Form(None),
        sun: bool = Form(False),
        mon: bool = Form(False),
        tue: bool = Form(False),
        wed: bool = Form(False),
        thu: bool = Form(False),
        fri: bool = Form(False),
        sat: bool = Form(False),
        content: str = Form(None),
        is_important: bool = Form(False),
        the_time: datetime.time = Form(None),
        weekly_task_id: int = Form(...),
        mode: str = Form(...)):

    user = get_user(demo_user, session)
    days = get_days_string(
        sun, mon, tue, wed, thu, fri, sat
    )

    weekly_task = weekly_task_from_input(
        user, title, days,
        content, the_time,
        is_important,
        weekly_task_id=weekly_task_id
    )

    fail_massage = None
    executed = False
    if mode == "add":
        fail_massage = "could not add The Weekly Task"
        # creating the weekly task
        created = create_weekly_task(
            user, weekly_task, session
        )
        executed = created

    else:  # mode == "edit"
        fail_massage = "These changes could not be made to the Weekly Task"
        # editing the weekly task
        edited = change_weekly_task(
            user, weekly_task, session
        )
        executed = edited

    if not executed:
        checked_days = get_checked_days(days)
        return templates.TemplateResponse("add_edit_weekly_task.html", {
            "request": request,
            "massage": fail_massage,
            "weekly_task": weekly_task,
            "mode": mode,
            "checked_days": checked_days
        })
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)
