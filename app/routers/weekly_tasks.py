import datetime

from fastapi import APIRouter, Depends, Request, Form
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.database.database import get_db
from app.database.models import User, WeeklyTask
from app.dependencies import templates
from app.internal.weekly_tasks import (
    remove_weekly_task, get_w_t_from_input,
    create_weekly_task, change_weekly_task)


router = APIRouter(
    prefix="/weekly-tasks",
    tags=["weekly-tasks"],
    responses={404: {"description": "Not found"}},
)


def get_placeholder_user():
    user = User(
        username='demo_user',
        email='demo@email.po',
        password='s3jsd183b13',
        full_name='The Demo'
    )
    return user


def get_user(demo_user, session):
    user = session.query(User).filter_by(username=demo_user.username).first()
    if not user:
        session.add(demo_user)
        session.commit()
        user = session.query(User).filter_by(id=1).first()
    return user


def get_checked_days(days=""):
    days_list = days.split(", ")
    day_names = {
        'Sun': 'Sunday',
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday'
    }
    checked_days = []
    for day, day_full_name in day_names.items():
        if day in days_list:
            day = day.lower()
            checked_days.append((day_full_name, day, "checked"))
        else:
            day = day.lower()
            checked_days.append((day_full_name, day, ""))
    return checked_days


def get_days(sun, mon, tue, wed, thu, fri, sat):
    days_dict = {
        "Sun": sun,
        "Mon": mon,
        "Tue": tue,
        "Wed": wed,
        "Thu": thu,
        "Fri": fri,
        "Sat": sat
    }
    days_list = [day for day, is_true in days_dict.items() if is_true]
    days = ", ".join(days_list)
    return days


@router.get("/")
def weekly_tasks_manager(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_placeholder_user)):

    user = get_user(demo_user, session)

    # TODO: Move the below function to a compatible location
    # Need to run regularly whenever there are no tasks on the week
    # Or will run on the background after the user left the
    # weekly-tasks manager page
    # function:
    # generate_tasks(session, user)  # imported from app.internal.weekly_tasks
    # session.close()

    return templates.TemplateResponse("weekly_tasks_manager.html", {
        "request": request,
        "weekly_tasks": user.weekly_tasks
    })


@router.get("/add")
def weekly_task_add(request: Request):

    checked_days = get_checked_days()
    return templates.TemplateResponse("add_edit_weekly_task.html", {
        "request": request,
        "weekly_task": None,
        "mode": "add",
        "checked_days": checked_days
    })


@router.post("/delete")
def weekly_task_remove(
        session=Depends(get_db),
        remove_id: int = Form(...)):

    remove_weekly_task(remove_id, session)
    session.close()
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/edit")
def weekly_task_edit(
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


@router.post("/make-change")
def weekly_task_make_change(
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
    days = get_days(
        sun, mon, tue, wed, thu, fri, sat
    )

    weekly_task = get_w_t_from_input(
        user,
        title, days,
        content, the_time,
        is_important,
        weekly_task_id=weekly_task_id
    )

    made_change = False
    massage = None
    if mode == "add":
        massage = "could not add The Weekly Task"
        made_change = create_weekly_task(
            user, session, weekly_task
        )
    else:  # mode == "edit"
        massage = "These changes could not be made to the Weekly Task"
        made_change = change_weekly_task(
            user, session, weekly_task
        )

    if not made_change:
        checked_days = get_checked_days(days)
        return templates.TemplateResponse("add_edit_weekly_task.html", {
            "request": request,
            "massage": massage,
            "weekly_task": weekly_task,
            "mode": mode,
            "checked_days": checked_days
        })
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)
