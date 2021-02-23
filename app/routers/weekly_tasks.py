import calendar
import datetime

from typing import List, Tuple, Optional
from fastapi import APIRouter, Cookie, Depends, Request, Response, Form
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND, HTTP_303_SEE_OTHER

from app.database.models import WeeklyTask
from app.dependencies import get_db, templates
from app.internal.security.dependencies import (
    current_user,
    schema,
    is_logged_in,
    current_user_from_db,
)
from app.internal.weekly_tasks import (
    remove_weekly_task,
    weekly_task_from_input,
    create_weekly_task,
    change_weekly_task,
)


router = APIRouter(
    prefix="/weekly-tasks",
    tags=["weekly-tasks"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_db)],
)


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
    sun: bool,
    mon: bool,
    tue: bool,
    wed: bool,
    thu: bool,
    fri: bool,
    sat: bool,
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
        "Sun": sun,
    }
    days_list = [day for day, is_checked in days_dict.items() if is_checked]
    days = ", ".join(days_list)
    return days


@router.get("/")
async def weekly_tasks_manager(
    request: Request,
    user: schema.CurrentUser = Depends(current_user_from_db),
):

    # TODO: Move the below function to a compatible location
    # Need to run regularly whenever there are tasks on the week
    # Or will run on the background after the user left the
    # weekly-tasks manager page
    # function:
    # generate_tasks(user, session)  # imported from app.internal.weekly_tasks
    # session.close()

    return templates.TemplateResponse(
        "weekly_tasks_manager.html",
        {"request": request, "weekly_tasks": user.weekly_tasks},
    )


@router.get("/add", dependencies=[Depends(is_logged_in)])
def add_weekly_task(request: Request):

    checked_days = get_checked_days()
    return templates.TemplateResponse(
        "add_edit_weekly_task.html",
        {
            "request": request,
            "weekly_task": None,
            "mode": "add",
            "checked_days": checked_days,
        },
    )


@router.delete("/", dependencies=[Depends(is_logged_in)])
def delete_weekly_task(remove_id: int, session: Session = Depends(get_db)):

    remove_weekly_task(remove_id, session)
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_303_SEE_OTHER)


@router.get("/edit", dependencies=[Depends(is_logged_in)])
def edit_weekly_task(edit_id: int, request: Request, session=Depends(get_db)):

    weekly_task = session.query(WeeklyTask).filter_by(id=edit_id).first()
    checked_days = get_checked_days(weekly_task.get_days())
    return templates.TemplateResponse(
        "add_edit_weekly_task.html",
        {
            "request": request,
            "weekly_task": weekly_task,
            "mode": "edit",
            "checked_days": checked_days,
        },
    )


def set_cookies(
    response: Response,
    id: Optional[int],
    title: Optional[str],
    content: Optional[str],
    days: str,
    is_important: bool,
) -> Response:
    """Sets the weekly task cookies
    for the failed/add and failed/edit routers"""
    if not id:
        id = 0
    response.set_cookie(key="id", value=id)
    response.set_cookie(key="title", value=title)
    response.set_cookie(key="content", value=content)
    response.set_cookie(key="days", value=days)
    response.set_cookie(key="is_important", value=is_important)
    return response


@router.post("/execute/{mode}")
def weekly_task_execute(
    request: Request,
    mode: str,
    session: Session = Depends(get_db),
    user: schema.CurrentUser = Depends(current_user_from_db),
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
):

    request.cookies.clear()

    days = get_days_string(sun, mon, tue, wed, thu, fri, sat)
    weekly_task = weekly_task_from_input(
        user,
        title,
        days,
        content,
        the_time,
        is_important,
        weekly_task_id=weekly_task_id,
    )

    if mode == "add":
        # creating the weekly task
        created = create_weekly_task(user, weekly_task, session)
        executed = created

    else:  # mode == "edit":
        # editing the weekly task
        edited = change_weekly_task(user, weekly_task, session)
        executed = edited

    if not executed:
        url = router.url_path_for("weekly_task_failed", mode=mode)
        html_respone = RedirectResponse(
            url=url,
            status_code=HTTP_303_SEE_OTHER,
        )
        response = set_cookies(
            html_respone,
            weekly_task.id,
            title,
            content,
            days,
            weekly_task.is_important,
        )
        return response

    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/failed/{mode}", response_class=HTMLResponse)
def weekly_task_failed(
    mode: str,
    request: Request,
    user: schema.CurrentUser = Depends(current_user),
    id: int = Cookie(0),
    title: str = Cookie(None),
    content: str = Cookie(None),
    days: str = Cookie(...),
    is_important: bool = Cookie(False),
):
    the_time = None
    if title == "None":
        title = None
    if content == "None":
        content = None
    weekly_task = weekly_task_from_input(
        user,
        title,
        days,
        content,
        the_time,
        is_important,
        id,
    )

    if mode == "add":
        fail_massage = "could not add The Weekly Task"
    else:
        fail_massage = "These changes could not be made to the Weekly Task"
    checked_days = get_checked_days(days)

    return templates.TemplateResponse(
        "add_edit_weekly_task.html",
        {
            "request": request,
            "massage": fail_massage,
            "weekly_task": weekly_task,
            "mode": mode,
            "checked_days": checked_days,
        },
    )
