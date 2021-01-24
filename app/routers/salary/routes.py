from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Request
from fastapi.param_functions import Depends
from sqlalchemy.sql.expression import and_

from app.database.models import SalarySettings, User
from app.dependencies import get_db, templates
from app.routers.salary.utils import calc_salary, create_default_settings, get_event_by_category, get_settings
from app.routers.profile import get_placeholder_user


router = APIRouter(
    prefix="/profile/salary",
    tags=["salary"],
)

# Code revision required after user login feature is added
def get_current_user() -> User:
    db = get_db()
    session = next(db)
    new_user = get_placeholder_user()
    user = session.query(User).filter_by(id=1).first()
    if not user:
        session.add(new_user)
        session.commit()
        user = session.query(User).filter_by(id=1).first()
    return user


def get_user_categories() -> Dict[int, str]:
    return {
        1: 'Workout',
        3: 'Flight',
        17: 'Going to the Movies',
        666: 'Lucy\'s Inferno',
    }


def get_holiday_categories() -> Dict[int, str]:
    return {
        1: 'Israel - Jewish',
        3: 'Iraq - Muslim',
        17: 'Cuba - Santeria',
        666: 'Hell - Satanist',
    }


@router.post("/new")
@router.get("/new")
async def create_settings(request: Request, session=Depends(get_db)) -> Any:
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    wage = create_default_settings()
    categories = get_user_categories()
    holidays = get_holiday_categories()

    form = await request.form()
    if form:
        user = get_current_user()
        category_id = form['category_id']
        settings = get_settings(user.id, category_id)

        if settings:
            return {
                "status": "failure",
                "message": "Settings for given user and category already exit",
            }

        settings = SalarySettings(
            user = user,
            category_id = category_id,
            wage = form['wage'],
            off_day = form['off_day'],
            holiday_category_id = form['holiday_category_id'],
            regular_hour_basis = form['regular_hour_basis'],
            night_hour_basis = form['night_hour_basis'],
            first_overtime_amount = form['first_overtime_amount'],
            first_overtime_pay = form['first_overtime_pay'],
            second_overtime_pay = form['second_overtime_pay'],
            week_working_hours = form['week_working_hours'],
            daily_transport = form['daily_transport'],
            pension = form['pension'],
            tax_points = form['tax_points'],
        )
        session.add(settings)
        session.commit()
        return {key: value for key, value in form.items()}

    return templates.TemplateResponse("salary/settings.j2", {
        'request': request,
        'wage': wage,
        'categories': categories,
        'holidays': holidays
    })


@router.post("/view")
@router.get("/view")
async def pick_category(request: Request) -> Any:
    pass


@router.post("/view/{category_id}")
@router.get("/view/{category_id}")
async def view_salary(request: Request, category_id: int) -> Any:
    # Code revision required after categories feature is added
    form = await request.form()
    user = get_current_user()
    wage = get_settings(user.id, category_id)

    if form:
        try:
            overtime = form['overtime']
        except KeyError:
            overtime = False
        year, month = map(int, form['month'].split('-'))
        month_name = date(1, month, 1).strftime("%b")
        salary = calc_salary(
            year=year, month=month, wage=wage, overtime=overtime,
            deduction=int(form['deduction']), bonus=int(form['bonus']),
        )
        category = get_user_categories()[category_id]
        return templates.TemplateResponse("salary/view.j2", {
            'request': request,
            'category': category,
            'month': month_name,
            'salary': salary,
            "wage": wage
        })
        #return {'salary': salary}

    shifts = get_event_by_category(category_id=category_id)
    start_date = shifts[0]['start']
    end_date = shifts[-1]['start']
    start = f"{start_date.year}-{str(start_date.month).zfill(2)}"
    end = f"{end_date.year}-{str(end_date.month).zfill(2)}"

    return templates.TemplateResponse("salary/month.j2", {
        'request': request,
        'start': start,
        'end': end,
    })