from fastapi import APIRouter, Depends, Request, HTTPException, Response, status
from app.dependencies import templates
from app.database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.internal.security.ouath2 import authenticate_user
from app.internal.security.ouath2 import LoginUser, create_jwt_token, check_jwt_token, oauth_schema, get_current_user
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.internal.security.schema import  Token
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


# @router.post('/login')
# async def login(
#         request: Request,
#         response: Response,
#         form: OAuth2PasswordRequestForm = Depends()):
#     form_dict = {'username': form.username, 'hashed_password': form.password}
#     user = LoginUser(**form_dict)
#     print(user)
#     if not user or not authenticate_user(user):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     jwt_token = create_jwt_token(user)
#     response = RedirectResponse(
#         url='/profile', status_code=HTTP_302_FOUND)
#     response.headers["Authorization"] = jwt_token

#     response.set_cookie(
#         "Authorization",
#         value=jwt_token,
#         httponly=True,
#         max_age=120,
#         expires=100,
#     )
#     return response
@router.post('/login')
async def login(request: Request, response: Response, form: OAuth2PasswordRequestForm = Depends()):
    form_dict = {'username': form.username, 'hashed_password': form.password}
    user = LoginUser(**form_dict)
    authenticated_user = authenticate_user(user)
    if not user or not authenticate_user(user):
        raise  HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    jwt_token = create_jwt_token(authenticated_user)
    # response.headers["Authorization"] = "Bearer " + jwt_token
    # user = authenticate_user()
    # return jwt_token
    jwt_token = create_jwt_token(user)
    print(jwt_token)
    response = RedirectResponse(
        url='/profile', status_code=HTTP_302_FOUND)
    response.headers["authorization"] = jwt_token
    return response
    
    
    response.set_cookie(key="access_token",value=f"Bearer {jwt_token}", httponly=True)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "User created",
        "status_code": 201})

# depends = check_jwt_token
@router.get('/protected')
async def protected_route(request: Request, jwt: str = Depends(get_current_user)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "protected"
    })