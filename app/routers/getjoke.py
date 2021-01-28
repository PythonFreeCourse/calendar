import requests
from fastapi import APIRouter


router = APIRouter()


@router.get("/getjoke")
def getjoke():
    return requests.get('http://api.icndb.com/jokes/random').json()
