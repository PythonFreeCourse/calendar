from typing import Optional, Union
from pydantic import BaseModel, validator, EmailStr, EmailError


EMPTY_FIELD_STRING = 'field is required'
MIN_FIELD_LENGTH = 3
MAX_FIELD_LENGTH = 20


def fields_not_empty(field: Optional[str]) -> Union[ValueError, str]:
    """Global function to validate fields are not empty."""
    if not field:
        raise ValueError(EMPTY_FIELD_STRING)
    return field


class UserBase(BaseModel):
    """
    Validating fields types
    Returns a User object without sensitive information
    """
    username: str
    email: str
    full_name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    """Validating fields types"""
    password: str
    confirm_password: str

    """
    Calling to field_not_empty validaion function,
    for each required field.
    """
    _fields_not_empty_username = validator(
        'username', allow_reuse=True)(fields_not_empty)
    _fields_not_empty_full_name = validator(
        'full_name', allow_reuse=True)(fields_not_empty)
    _fields_not_empty_password = validator(
        'password', allow_reuse=True)(fields_not_empty)
    _fields_not_empty_confirm_password = validator(
        'confirm_password', allow_reuse=True)(fields_not_empty)
    _fields_not_empty_email = validator(
        'email', allow_reuse=True)(fields_not_empty)

    @validator('confirm_password')
    def passwords_match(
            cls, confirm_password: str,
            values: UserBase) -> Union[ValueError, str]:
        """Validating passwords fields identical."""
        if 'password' in values and confirm_password != values['password']:
            raise ValueError("doesn't match to password")
        return confirm_password

    @validator('username')
    def username_length(cls, username: str) -> Union[ValueError, str]:
        """Validating username length is legal"""
        if not (MIN_FIELD_LENGTH < len(username) < MAX_FIELD_LENGTH):
            raise ValueError("must contain between 3 to 20 charactars")
        return username

    @validator('password')
    def password_length(cls, password: str) -> Union[ValueError, str]:
        """Validating username length is legal"""
        if not (MIN_FIELD_LENGTH < len(password) < MAX_FIELD_LENGTH):
            raise ValueError("must contain between 3 to 20 charactars")
        return password

    @validator('email')
    def confirm_mail(cls, email: str) -> Union[ValueError, str]:
        """Validating email is valid mail address."""
        try:
            EmailStr.validate(email)
            return email
        except EmailError:
            raise ValueError("address is not valid")


class User(UserBase):
    """
    Validating fields types
    Returns a User object without sensitive information
    """
    id: int
    is_active: bool
