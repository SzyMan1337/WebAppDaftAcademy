from fastapi import FastAPI, Response, status
from datetime import date, datetime
from datetime import timedelta
from pydantic import BaseModel
import hashlib

app = FastAPI()
app.i = 0
app.dicc = {}

class HelloResp(BaseModel):
    id:int
    name:str
    surname:str
    register_date:str
    vaccination_date:str


@app.get("/")
def root():
    return {"message": "Hello world!"}

@app.get("/method")
def method_get():
    return {"method": "GET"}

@app.put("/method")
def method_put():
    return {"method": "PUT"}

@app.delete("/method")
def method_del():
    return {"method": "DELETE"}

@app.options("/method")
def method_opt():
    return {"method": "OPTIONS"}

@app.post("/method", status_code=201)
def method_post():
    return {"method": "POST"}

@app.get("/auth",status_code=401)
async def authMet(password:str = None, password_hash:str =None, respose:Response=Response()):
    if password != None and password != "":
        m = hashlib.sha512(str(password).encode('utf-8')).hexdigest()
        if(m == password_hash):
            respose.status_code = 204


class Item(BaseModel):
    name:str
    surname:str


@app.post("/register", status_code=201)
def registerPost(item:Item = None):
    if item != None:
        app.i = app.i + 1
        dlugos = 0
        if(item.name != None):
            dlugos = len(item.name)
        if(item.surname != None):
            dlugos = dlugos + +len(item.surname)
        today = datetime.now()
        day2 = today + timedelta(days=dlugos)
        p = today.strftime("%Y-%m-%d")
        d=day2.strftime("%Y-%m-%d")
        x = HelloResp(id=1, name=f"{item.name}", surname=f"{item.surname}", register_date= f"{p}", vaccination_date= f"{d}")
        app.dicc[app.i] = x
        return x
       
@app.get("/register/{id}", status_code = 200)
def getPost(id:int, respose:Response=Response()):
    if id <1:
        respose.status_code = 400
    elif app.dicc.has_key(id):
        return app.dicc[id]
    else:
        response.status_code = 404
    