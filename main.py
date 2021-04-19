from fastapi import FastAPI, Response, status
from datetime import date, datetime
from datetime import timedelta
from pydantic import BaseModel
import hashlib

app = FastAPI()
app.i = 0

app.id = 0
app.patients = []

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

class Person(BaseModel):
    name: str
    surname: str

class MessageResp(BaseModel):
    message: str


class MethodResp(BaseModel):
    method: str

class Patient(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


def id_inc():
    app.id += 1
    return app.id


@app.post("/register", response_model=Patient, status_code=status.HTTP_201_CREATED)
def register(person: Person):
    plainname = ''.join(filter(str.isalpha, person.name))
    plainsurname = ''.join(filter(str.isalpha, person.surname))
    new_patient = Patient(id=id_inc(),
                   name=person.name,
                   surname=person.surname,
                   register_date=date.today().strftime("%Y-%m-%d"),
                   vaccination_date=(date.today() + timedelta(days=len(plainname) + len(plainsurname))).strftime("%Y-%m-%d"))

    app.patients.append(new_patient)
    return new_patient


@app.get("/patient/{id}", response_model=Patient)
def patient(id: int, response: Response):
    if id < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    if id > len(app.patients):
        response.status_code = status.HTTP_404_NOT_FOUND
        return

    response.status_code = status.HTTP_200_OK
    return app.patients[id - 1].dict()
    