import datetime

from fastapi import APIRouter, Depends, Request
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
    user_titles = (weekly_tasks.title for weekly_tasks in user.weekly_tasks)
    if weekly_task.title in user_titles:
        return False
    session.add(weekly_task)
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


def set_demo_weekly_task(user, session):
    weekly_task_demo_1 = WeeklyTask(
        title="demo_test1",
        days="Sun, Tue",
        content="make the demo test 1",
        is_important=True,
        the_time="14:00",
        owner_id=user.id
    )
    weekly_task_demo_2 = WeeklyTask(
        title="demo_test2",
        days="Wed, Fri",
        content="make the demo test 2",
        is_important=False,
        the_time="16:00",
        owner_id=user.id
    )

    make_weekly_task(weekly_task_demo_1, user, session)
    make_weekly_task(weekly_task_demo_2, user, session)


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


def remove_weekly_task(weekly_task, session):
    if weekly_task:
        session.query(WeeklyTask).filter_by(id=weekly_task.id).delete()
        session.commit()
        return True
    return False


@router.get("/demo/remove")
async def weekly_tasks_demo_remove(
        session=Depends(get_db),
        demo_user=Depends(get_demo_user)):
    
    user = get_user(demo_user, session)
    weekly_task = user.weekly_tasks
    if weekly_task:
        weekly_task = weekly_task[0]
    removed = remove_weekly_task(weekly_task, session)

    return {"weekly_tasks_demo_remove": removed}


@router.get("/demo")
async def weekly_tasks_demo(
        session=Depends(get_db),
        demo_user=Depends(get_demo_user)):
    
    user = get_user(demo_user, session)
    set_demo_weekly_task(user, session)
    return {"set_demo_weekly_task": "True"}


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


@router.post("/add-weeklytask")
async def weekly_task_make_add(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_demo_user)):
    
    user = get_user(demo_user, session)
    data = await request.form()

    weekly_task = WeeklyTask(
        title=data['title'],
        days=data['days'],
        content=data['content'],
        is_important=data['is_important'],
        the_time=data['the_time'],
        owner_id=user.id
    )

    made = make_weekly_task(weekly_task, user, session)
    if not made:
        massage = "could not add The Weekly Task"
        return templates.TemplateResponse("add_weekly_task.html", {
        "request": request,
        "massage": massage
        })

    url = router.url_path_for("weekly-tasks")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/add")
async def weekly_task_add(
        request: Request,):

    return templates.TemplateResponse("add_weekly_task.html", {
        "request": request
    })


@router.post("/edit-weeklytask")
async def weekly_task_make_edit(
        request: Request,
        session=Depends(get_db),
        demo_user=Depends(get_demo_user)):
    
    user = get_user(demo_user, session)
    data = await request.form()

    weekly_task = WeeklyTask(
        title=data['title'],
        days=data['days'],
        content=data['content'],
        is_important=data['is_important'],
        the_time=data['the_time'],
        owner_id=user.id
    )

    made = make_weekly_task(weekly_task, user, session)

    if not made:
        massage = "These changes could not be made to the Weekly Task"
        return templates.TemplateResponse("add_weekly_task.html", {
        "request": request,
        "massage": massage,
        "weekly_task": weekly_task
        })

    session.query(WeeklyTask).filter_by(id=data['id']).delete()
    session.commit()
    url = router.url_path_for("weekly-tasks")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/edit")
async def weekly_task_edit(
        request: Request,
        session=Depends(get_db),):

    data = await request.form()
    weekly_task = session.query(WeeklyTask).filter_by(id=data['id']).first

    return templates.TemplateResponse("add_weekly_task.html", {
        "request": request,
        "weekly_task": weekly_task
    })