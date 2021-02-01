from fastapi import APIRouter, Depends, Request, HTTPException, Response, status
from app.dependencies import templates
from app.database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.internal.security.ouath2 import authenticate_user
from app.internal.security.ouath2 import LoginUser, create_jwt_token, check_jwt_token, oauth_schema, current_user, get_cookie, logged_in_user
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.internal.security.schema import  Token
from starlette.status import HTTP_401_UNAUTHORIZED
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
    return templates.TemplateResponse("login.html", {
        "request": request,
        "errors": None
    })




@router.post('/login')
async def login(
        request: Request,
        response: Response,
        form: OAuth2PasswordRequestForm = Depends()):
    form_dict = {'username': form.username, 'hashed_password': form.password}
    user = LoginUser(**form_dict)
    # print(user)
    if user:
        user = authenticate_user(user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    jwt_token = create_jwt_token(user)
    response = RedirectResponse(url="/protected", status_code=HTTP_302_FOUND) 
    response.set_cookie(
        "Authorization",
        value=jwt_token,
        httponly=True,
    )
    return response


@router.get('/logout')
async def login(request: Request):
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND) 
    response.delete_cookie("Authorization")
    # raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return response


@router.get('/protected')
async def protected_route(request: Request, user: User = Depends(current_user)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": user.username
    })

@router.get('/user')
async def user_route(request: Request, current_user: User = Depends(logged_in_user)):
    print(current_user)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "user.username"
    })