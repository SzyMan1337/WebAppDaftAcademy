from fastapi import FastAPI, Response, status
from datetime import date
from datetime import timedelta
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

@app.get("/auth/{password}/{password_hash}",status_code=201)
def authMet(password:str, password_hash:str, respose:Response):
    m = hashlib.sha512(str(password).encode('utf-8')).hexdigest()
    if(m != password_hash):
        respose.status_code = status.HTTP_404_UNAUTHORIZED


# @app.post("/register/{name}/{surname}", status_code=201)
# def registerPost(name:str, surname:str):
#     app.i = app.i +1
#     dlugos = len(name)+len(surname)
#     today = date.today
#     day2 = today - timedelta(days=dlugos); 
#     return {"id": 1, "name": f"{name}", "register_date": f"{today.strftime("%Y-%m-%d")}", "vaccination_date": f"{day2.strftime("%Y-%m-%d")}"}

