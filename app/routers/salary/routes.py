from datetime import date
from typing import Dict

from fastapi import APIRouter, Request
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse, Response

from app.database.models import SalarySettings
from app.dependencies import get_db, templates
from app.internal.utils import create_model, get_current_user
from app.routers.salary import utils

router = APIRouter(
    prefix='/salary',
    tags=['salary'],
    dependencies=[Depends(get_db)],
)


def get_user_categories() -> Dict[int, str]:
    """Mock function for user relevant category search."""
    # Code revision required after categories feature is added
    return {
        1: 'Workout',
        17: 'Flight',
        42: 'Going to the Movies',
        666: 'Lucy\'s Inferno',
    }


def get_holiday_categories() -> Dict[int, str]:
    """Mock function for user relevant holiday category search."""
    # Code revision required after holiday times feature is added
    return {
        1: 'Israel - Jewish',
        3: 'Iraq - Muslim',
        17: 'Cuba - Santeria',
        666: 'Hell - Satanist',
    }


def get_salary_categories(session: Session, user_id: int,
                          existing: bool = True) -> Dict[int, str]:
    """Returns a dict of all categories the user has created salary settings
    for. If `existing` is False, a dict with all the categories the user has
    defined but yet to create a salary setting for is returned.

    Args:
        user_id (int): Id of the relevant user.
        existing (bool, optional): Wether to return categories of existing
                                   salary setting, or all other user relevant
                                   categories.

    Returns:
        dict(int, str): All categories the user has created salary settings
                        for if `existing` is True, all other categories
                        otherwise.

    Raises:
        None
    """
    categories = {}
    for key, value in get_user_categories().items():
        settings = utils.get_settings(session, user_id, key)
        if settings:
            is_settings = True
        else:
            is_settings = False
        if existing == is_settings:
            categories[key] = value
    return categories


@router.get('/')
def salary_home(session: Session = Depends(get_db)) -> Response:
    """Redirects user to salary view page if any salary settings exist, and to
    settings creation page otherwise."""
    user = get_current_user(session)
    if get_salary_categories(session, user.id):
        return RedirectResponse(router.url_path_for('pick_category'))

    return RedirectResponse(router.url_path_for('create_settings'))


@router.post('/new')
@router.get('/new')
async def create_settings(request: Request,
                          session: Session = Depends(get_db)) -> Response:
    """Renders a salary settings creation page with all available user related
    categories and default settings. Creates salary settings according to form
    and redirects to salary view page upon submition."""
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    user = get_current_user(session)
    wage = utils.DEFAULT_SETTINGS
    categories = get_salary_categories(session, user.id, False)
    holidays = get_holiday_categories()

    form = await request.form()
    if form:
        category_id = int(form['category_id'])

        settings = {
            'user_id': user.id,
            'category_id': category_id,
            'wage': form['wage'],
            'off_day': form['off_day'],
            'holiday_category_id': form['holiday_category_id'],
            'regular_hour_basis': form['regular_hour_basis'],
            'night_hour_basis': form['night_hour_basis'],
            'night_start': utils.get_time_from_string(form['night_start']),
            'night_end': utils.get_time_from_string(form['night_end']),
            'night_min_len': utils.get_time_from_string(form['night_min_len']),
            'first_overtime_amount': form['first_overtime_amount'],
            'first_overtime_pay': form['first_overtime_pay'],
            'second_overtime_pay': form['second_overtime_pay'],
            'week_working_hours': form['week_working_hours'],
            'daily_transport': form['daily_transport'],
        }

        create_model(session, SalarySettings, **settings)

        return RedirectResponse(router.url_path_for(
            'view_salary', category_id=str(category_id)))

    return templates.TemplateResponse('salary/settings.j2', {
        'request': request,
        'wage': wage,
        'categories': categories,
        'holidays': holidays
    })


@router.post('/edit')
@router.get('/edit')
async def pick_settings(request: Request,
                        session: Session = Depends(get_db)) -> Response:
    """Renders a category salary settings edit choice page, redirects to the
    relevant salary settings edit page upon submition, or to settings creation
    page if none exist."""
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    form = await request.form()
    user = get_current_user(session)
    categories = get_salary_categories(session, user.id)

    if form:
        category = form['category_id']
        return RedirectResponse(router.url_path_for('edit_settings',
                                                    category_id=category))

    if categories:
        return templates.TemplateResponse('salary/pick.j2', {
            'request': request,
            'categories': categories,
            'edit': True,
        })

    return RedirectResponse(router.url_path_for('create_settings'))


@router.post('/edit/{category_id}')
@router.get('/edit/{category_id}')
async def edit_settings(request: Request, category_id: int,
                        session: Session = Depends(get_db)) -> Response:
    """Renders a salary settings edit page for setting corresponding to
    logged-in user and `category_id`. Edits the salary settings according to
    form and redirects to month choice pre calculation display page upon
    submition. Redirects to category salary settings edit choice
    page if settings don't exist."""
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    form = await request.form()
    user = get_current_user(session)
    wage = utils.get_settings(session, user.id, category_id)
    holidays = get_holiday_categories()

    try:
        category = get_user_categories()[category_id]

    except (AttributeError, KeyError):
        return RedirectResponse(router.url_path_for('pick_settings'))

    if utils.update_settings(session, wage, form):
        return RedirectResponse(router.url_path_for(
            'view_salary', category_id=str(category_id)))

    else:
        if wage:
            return templates.TemplateResponse('salary/settings.j2', {
                'request': request,
                'wage': wage,
                'category': category,
                'category_id': category_id,
                'holidays': holidays
            })

        return RedirectResponse(router.url_path_for('pick_settings'))


@router.post('/view')
@router.get('/view')
async def pick_category(request: Request,
                        session: Session = Depends(get_db)) -> Response:
    """Renders a category salary calculation view choice page, redirects to the
    relevant salary calculation view page upon submition, or to settings
    creation page if no salary settings exist."""
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    form = await request.form()
    user = get_current_user(session)
    categories = get_salary_categories(session, user.id)

    if form:
        category = form['category_id']
        return RedirectResponse(router.url_path_for('view_salary',
                                                    category_id=category))

    if categories:
        return templates.TemplateResponse('salary/pick.j2', {
            'request': request,
            'categories': categories,
        })

    return RedirectResponse(router.url_path_for('create_settings'))


@router.post('/view/{category_id}')
@router.get('/view/{category_id}')
async def view_salary(request: Request, category_id: int,
                      session: Session = Depends(get_db)) -> Response:
    """Renders month choice pre calculation display page. Overtime, additions &
    deductions to be calculated can be provided. Displays calculation details
    upon submition. Redirects to category salary calculation view choice page
    if salary settings don't exist for logged-in user and `category_id`."""
    # Code revision required after user login feature is added
    # Code revision required after categories feature is added
    form = await request.form()
    user = get_current_user(session)
    wage = utils.get_settings(session, user.id, category_id)

    try:
        category = get_user_categories()[category_id]

    except KeyError:
        return RedirectResponse(router.url_path_for('pick_category'))

    try:  # try block prevents crashing upon redirection to the page.
        try:
            overtime = form['overtime']

        except KeyError:
            overtime = ''

        year, month = map(int, form['month'].split('-'))
        month_name = date(1, month, 1).strftime('%b')
        salary = utils.calc_salary(
            year=year, month=month, wage=wage, overtime=bool(overtime),
            deduction=int(form['deduction']), bonus=int(form['bonus']),
        )

        return templates.TemplateResponse('salary/view.j2', {
            'request': request,
            'category': category,
            'category_id': category_id,
            'month': month_name,
            'salary': salary,
            'wage': wage
        })

    except KeyError:
        if wage:
            shifts = utils.get_event_by_category(category_id=category_id)
            start_date = shifts[0].start
            end_date = shifts[-1].start
            start = f'{start_date.year}-{str(start_date.month).zfill(2)}'
            end = f'{end_date.year}-{str(end_date.month).zfill(2)}'

            return templates.TemplateResponse('salary/month.j2', {
                'request': request,
                'category': category,
                'category_id': category_id,
                'start': start,
                'end': end,
            })

        return RedirectResponse(router.url_path_for('pick_category'))
