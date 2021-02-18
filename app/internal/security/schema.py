from typing import Optional, Union

from pydantic import BaseModel, validator


class CurrentUser(BaseModel):
    """
    Validating fields types
    Returns a user details as a class.
    """
    user_id: Optional[int]
    username: str

    class Config:
        orm_mode = True


class LoginUser(CurrentUser):
    """
    Validating fields types
    Returns a User object for signing in.
    """
    is_manager: Optional[bool]
    password: str


class ForgotPassword(BaseModel):
    """
    BaseModel for collecting and verifying user
    details sending a token via email
    """
    username: str
    email: str
    user_id: Optional[str] = None
    token: Optional[str] = None
    is_manager: Optional[bool] = False

    class Config:
        orm_mode = True

    @validator('username')
    def password_length(cls, username: str) -> Union[ValueError, str]:
        """Validating username length is legal"""
        if not (MIN_FIELD_LENGTH < len(username) < MAX_FIELD_LENGTH):
            raise ValueError
        return username


MIN_FIELD_LENGTH = 3
MAX_FIELD_LENGTH = 20


class ResetPassword(BaseModel):
    """
    Validating fields types
    """
    username: str
    password: str
    confirm_password: str

    class Config:
        orm_mode = True

    @validator('confirm_password')
    def passwords_match(
            cls, confirm_password: str,
            values: BaseModel) -> Union[ValueError, str]:
        """Validating passwords fields identical."""
        if 'password' in values and confirm_password != values['password']:
            raise ValueError
        return confirm_password

    @validator('password')
    def password_length(cls, password: str) -> Union[ValueError, str]:
        """Validating password length is legal"""
        if not (MIN_FIELD_LENGTH < len(password) < MAX_FIELD_LENGTH):
            raise ValueError
        return password
