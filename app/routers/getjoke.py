from fastapi import APIRouter
import requests


router = APIRouter()


@router.get("/getjoke")
def getjoke():
    return requests.get(f'http://api.icndb.com/jokes/random').json()
