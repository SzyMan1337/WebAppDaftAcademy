from fastapi import FastAPI, Response, status
from datetime import date, datetime
from datetime import timedelta
from pydantic import BaseModel
import hashlib

app = FastAPI()
app.i = 0

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

@app.post("/register", status_code=201)
async def registerPost(name:str = None, surname:str = None):
    app.i = app.i + 1
    dlugos = len(name)+len(surname)
    today = datetime.now()
    day2 = today - timedelta(days=dlugos)
    p= today.strftime("%Y-%m-%d")
    d=day2.strftime("%Y-%m-%d")
    return {"id": 1, "name": f"{name}", "register_date": f"{p}", "vaccination_date": f"{d}"}

