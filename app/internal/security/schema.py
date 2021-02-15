from typing import Optional

from pydantic import BaseModel


class LoginUser(BaseModel):
    """
    Validating fields types
    Returns a User object for signing in.
    """
    user_id: Optional[int]
    is_manager: Optional[bool]
    username: str
    password: str

    class Config:
        orm_mode = True
