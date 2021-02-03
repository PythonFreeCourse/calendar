from pydantic import BaseModel


class LoginUser(BaseModel):
    '''
    Validating fields types
    Returns a User object for signing in.
    '''
    username: str
    hashed_password: str

    class Config:
        orm_mode = True
