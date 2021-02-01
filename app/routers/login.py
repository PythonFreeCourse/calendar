from fastapi import APIRouter, Depends, Request, Response
from app.dependencies import templates
from fastapi.security import OAuth2PasswordRequestForm
from app.internal.security.ouath2 import authenticate_user
from app.internal.security.ouath2 import LoginUser, create_jwt_token, check_jwt_token
from app.internal.security.dependancies import current_user_required, current_user
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.database.models import User


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
    message = ""
    if 'message' in request.cookies:
        message = request.cookies['message']
    return templates.TemplateResponse("login.html", {
        "request": request,
        "errors": None,
        "message": message
    })


@router.post('/login')
async def login(
        request: Request,
        response: Response,
        form: OAuth2PasswordRequestForm = Depends()):
    url = "/"
    form_dict = {'username': form.username, 'hashed_password': form.password}
    user = LoginUser(**form_dict)
    if user:
        user = authenticate_user(user)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "errors": None,
            "message": 'Please check your credentials'
        })

    ### check url
    if 'next_url' in request.cookies:
        url = request.cookies['next_url']

    jwt_token = create_jwt_token(user)
    response = RedirectResponse(url=url, status_code=HTTP_302_FOUND) 
    response.set_cookie(
        "Authorization",
        value=jwt_token,
        httponly=True,
    )
    response.delete_cookie('next_url')
    response.delete_cookie('message')
    return response


@router.get('/logout')
async def login(request: Request):
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND) 
    response.delete_cookie("Authorization")
    return response


@router.get('/protected')
async def protected_route(request: Request, user: User = Depends(current_user_required)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": user.username
    })

@router.get('/user')
async def user_route(request: Request, current_user: User = Depends(current_user)):
    print(current_user.username)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "user.username"
    })