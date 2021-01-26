import datetime

from fastapi import APIRouter, Depends, Request, Form
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.database.database import get_db
from app.database.models import User, Task, WeeklyTask
from app.dependencies import templates


router = APIRouter(
    prefix="/weekly-tasks",
    tags=["weekly-tasks"],
    responses={404: {"description": "Not found"}},
)


def get_demo_user():
    user = User(
        username='demo_user',
        email='demo@email.po',
        password='s3jsd183b13',
        full_name='The Demo'
    )
    return user


def make_weekly_task(weekly_task, user, session):
    
    # make more Conditions

    user_titles = (weekly_tasks.title for weekly_tasks in user.weekly_tasks)
    if weekly_task.title in user_titles:
        return False

    session.add(weekly_task)
    session.commit()
    return True


def change_weekly_task(weekly_task, user, session):

    # make more Conditions

    if not weekly_task.owner_id == user.id:
        return False
    
    old_weekly_task = session.query(WeeklyTask).filter_by(id=weekly_task.id).first()
    old_weekly_task.title = weekly_task.title
    old_weekly_task.days = weekly_task.days
    old_weekly_task.content = weekly_task.content
    old_weekly_task.is_important = weekly_task.is_important
    old_weekly_task.the_time = weekly_task.the_time
    session.commit()
    return True


def make_task(task, user, session):
    user_tasks_query = session.query(Task).filter_by(owner_id=user.id)
    same_date_task = user_tasks_query.filter_by(date_time=task.date_time).first()
    if not same_date_task:
        session.add(task)
        session.commit()
        return True
    return False


def generate_tasks(session, user):
    
    current_date = datetime.date.today()
    current_week_num = current_date.strftime("%W")
    current_year = current_date.strftime("%Y")

    for weekly_task in user.weekly_tasks:
        the_time = weekly_task.the_time
        days = weekly_task.days.split(", ")
        for day in days:
            date_string = f"{day} {the_time} {current_week_num} {current_year}"
            date_time = datetime.datetime.strptime(date_string, "%a %H:%M %W %Y")
            task = Task(
                title=weekly_task.title,
                content=weekly_task.content,
                is_done=False,
                is_important=weekly_task.is_important,
                date_time=date_time,
                owner_id=user.id
            )
            make_task(task, user, session)


def get_user(demo_user, session):
    user = session.query(User).filter_by(username=demo_user.username).first()
    if not user:
        session.add(demo_user)
        session.commit()
        user = session.query(User).filter_by(id=1).first()
    return user


def remove_weekly_task(weekly_task_id, session):
    weekly_task = session.query(WeeklyTask).filter_by(id=weekly_task_id).first()
    if weekly_task:
        session.query(WeeklyTask).filter_by(id=weekly_task_id).delete()
        session.commit()
        return True
    return False


@router.get("/")
async def weekly_tasks_manager(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_demo_user)):
    
    user = get_user(demo_user, session)
    generate_tasks(session, user)

    return templates.TemplateResponse("weekly_tasks_manager.html", {
        "request": request,
        "weekly_tasks": user.weekly_tasks
    })


@router.get("/add")
async def weekly_task_add(
        request: Request):

    return templates.TemplateResponse("add_edit_weekly_task.html", {
        "request": request,
        "weekly_task": None,
        "mode": "add"
    })


@router.post("/remove")
async def weekly_task_remove(
        request: Request,
        session=Depends(get_db),
        remove_id: int = Form(...)):

    removed = remove_weekly_task(remove_id, session)
    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/edit")
async def weekly_task_edit(
        request: Request,
        session=Depends(get_db),
        edit_id: int = Form(...)):

    weekly_task = session.query(WeeklyTask).filter_by(id=edit_id).first()

    return templates.TemplateResponse("add_edit_weekly_task.html", {
        "request": request,
        "weekly_task": weekly_task,
        "mode": "edit"
    })

@router.post("/make-change")
async def weekly_task_make_change(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_demo_user),
        title: str = Form(...),
        sun: bool = Form(False),
        mon: bool = Form(False),
        tue: bool = Form(False),
        wed: bool = Form(False),
        thu: bool = Form(False),
        fri: bool = Form(False),
        sat: bool = Form(False),
        content: str = Form(...),
        is_important: bool = Form(False),
        the_time: datetime.time = Form(...),
        weekly_task_id: int = Form(...),
        mode: str = Form(...)):
    
    user = get_user(demo_user, session)

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

    weekly_task = WeeklyTask(
        title=title,
        days=days,
        content=content,
        is_important=is_important,
        the_time=the_time.strftime("%H:%M"),
        owner_id=user.id
    )
    if weekly_task_id:
        weekly_task.id = weekly_task_id


    if mode == "add":
        made = make_weekly_task(weekly_task, user, session)
        if not made:
            massage = "could not add The Weekly Task"
            return templates.TemplateResponse("add_edit_weekly_task.html", {
                "request": request,
                "massage": massage,
                "weekly_task": weekly_task,
                "mode": mode
            })
    else:
        changed = change_weekly_task(weekly_task, user, session)
        if not changed:
            massage = "These changes could not be made to the Weekly Task"
            return templates.TemplateResponse("add_edit_weekly_task.html", {
                "request": request,
                "massage": massage,
                "weekly_task": weekly_task,
                "mode": mode
            })

    url = router.url_path_for("weekly_tasks_manager")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)