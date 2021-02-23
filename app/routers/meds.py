from datetime import date, time, timedelta

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.status import HTTP_303_SEE_OTHER

from app.dependencies import get_db, templates
from app.internal import meds
from app.internal.utils import get_current_user
from app.main import app


router = APIRouter(
    prefix='/meds',
    tags=['meds'],
    dependencies=[Depends(get_db)],
)


@router.get('/')
@router.post('/')
async def medications(request: Request,
                      session: Session = Depends(get_db)) -> Response:
    """Renders medication reminders creation form page. Creates reminders in DB
    and redirects to home page upon submition if valid."""
    form = await request.form()
    errors = []

    form_data = {
        'name': '',
        'start': date.today(),
        'first': None,
        'end': date.today() + timedelta(days=7),
        'amount': 1,
        'early': time(8),
        'late': time(22),
        'min': time(0, 1),
        'max': time(23, 59),
        'note': '',
    }

    if form:
        form, form_data = meds.trans_form(form)
        user = get_current_user(session)
        errors = meds.validate_form(form)
        if not errors:
            meds.create_events(session, user.id, form)
            return RedirectResponse(app.url_path_for('home'),
                                    status_code=HTTP_303_SEE_OTHER)

    return templates.TemplateResponse('meds.j2', {
        'request': request,
        'errors': errors,
        'data': form_data,
        'quantity': meds.MAX_EVENT_QUANTITY,
    })
