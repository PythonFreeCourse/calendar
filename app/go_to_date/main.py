from fastapi import FastAPI
from typing import Optional
import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/component/{component}")
async def return_comp(component: int):
    return {"component": component}

@app.get("/component")
async def param(num: int, msg: Optional[str]):
    return {"component": num, "msg": msg}