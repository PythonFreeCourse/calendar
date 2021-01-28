from app.internal import user
from app.database import schemas
from app.database.database import get_db
from app.dependencies import templates
from fastapi import APIRouter, Depends, Request, Response
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.internal.security.security_main import fastapi_users


router = APIRouter(
    prefix="",
    tags=["register"],
    responses={404: {"description": "Not found"}},
)

# router = fastapi_users.get_register_router()


@router.get("/register")
async def register_user_form(request: Request) -> templates:
    '''
    rendering register route get method
    '''
    return templates.TemplateResponse("register.html", {
        "request": request,
        "errors": None
    })


# @router.post("/register")
# async def register(
#                 request: Request, response: Response, db: Session = Depends(get_db)) -> templates:
#     '''
#     rendering register route post method.
#     '''
#     form = await request.form()
#     form_dict = dict(form)
    
#     try:
#         # creating pydantic schema object out of form data

#         new_user = schemas.UserCreate(**form_dict)
#     except ValidationError as e:
#         # if pydantic validations fails, rendering errors to register.html

#         errors = {error['loc'][0]: " ".join((
#             error['loc'][0].capitalize(),
#             error['msg'])) for error in e.errors()}
#         return templates.TemplateResponse("register.html", {
#             "request": request,
#             "errors": errors,
#             "form_values": form_dict})
#     errors = {}
#     db_user_email = user.get_by_mail(db, email=new_user.email)
#     db_user_username = user.get_by_username(
#         db, username=new_user.username)
#     if db_user_username:
#         errors['username'] = "That username is already taken"
#     if db_user_email:
#         errors['email'] = "Email already registered"
#     if errors:
#         return templates.TemplateResponse("register.html", {
#             "request": request,
#             "errors": errors,
#             "form_values": form_dict})

#     del form_dict['confirm_password']
#     form_dict["is_active"] = True
#     form_dict["is_superuser"] = False
#     form_dict["is_verified"] = False
#     print(form_dict)    
#     return
#     import httpx

#     # res = httpx.post('http://127.0.0.1:8000/auth/register', data=form_dict)
    
#     # async with httpx.AsyncClient() as client:
#     #     await client.post('/auth/register', data=form_dict)
#     r = httpx.get("https://localhost:8000/auth/register", verify="/tmp/client.pem", data=form_dict)
#     # with httpx.Client() as client:
#     #     await client.post('http://127.0.0.1:8000/auth/register', data=form_dict)
 
   

    
    # response = RedirectResponse(
    #     url='/auth/register', status_code=307)
    # # import json
    # # response.body = json.dumps(form_dict)
    # response.body = form_dict
    # return response
    
    
    return response
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "User created",
        "status_code": 201})
