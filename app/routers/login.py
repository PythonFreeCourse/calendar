from fastapi import APIRouter, Depends, Request, HTTPException
from app.dependencies import templates
from app.database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.internal.security.ouath2 import authenticate_user
from app.internal.security.ouath2 import LoginUser, create_jwt_token, check_jwt_token
from starlette.status import HTTP_401_UNAUTHORIZED


router = APIRouter(
    prefix="",
    tags=["/login"],
    responses={404: {"description": "Not found"}},
)

@router.get("/login")
async def login_user_form(request: Request) -> templates:
    '''
    rendering register route get method
    '''
    return templates.TemplateResponse("login.html", {
        "request": request,
        "errors": None
    })

@router.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # form = await request.form()
    # form_username = form.username
    # form_password = form.password
    form_dict = {'username': form.username, 'hashed_password': form.password}
    # user = LoginUser(form_username, form_password)
    user = LoginUser(**form_dict)
    # print(user)
    if not user or not authenticate_user(user):
        raise  HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    jwt_token = create_jwt_token(user)
    # user = authenticate_user()
    return {'token': jwt_token}


@router.get('/protected')
async def protected_route(request: Request, jwt: bool = Depends(check_jwt_token)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "protected"
    })