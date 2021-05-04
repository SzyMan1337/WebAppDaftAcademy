import secrets
from datetime import date, datetime, timedelta
from fastapi import Cookie, Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from hashlib import sha256, sha512
from pydantic import BaseModel
from typing import Dict, Optional

class Patient(BaseModel):
    id: Optional[int] = 1
    name: str
    surname: str
    register_date: Optional[date]
    vaccination_date: Optional[date]

class Message:
    def __init__(self, format: Optional[str] = Query("")):
        self.format = format
        self.word = ""

    def return_message(self):
        '''Return message in correct format (json/html/plain)'''
        if self.format == "json":
            message = {"message": f"{self.word}!"}
        elif self.format == "html":
            message = HTMLResponse(f"<h1>{self.word}!</h1>", status_code=200)
        else:
            message = PlainTextResponse(f"{self.word}!", status_code=200)
        return message

app = FastAPI()
app.counter: int = 1
app.mount("/static", StaticFiles(directory="static"), name="static")
app.session_cookie_tokens = []
app.session_tokens = []
app.storage: Dict[int, Patient] = {}
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

#1.1
@app.get("/")
def root():
    return {"message": "Hello world!"}

#1.2
@app.api_route(path = "/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], status_code = 200)
def read_request(request: Request, response: Response):
    if request.method == "POST":
        response.status_code = status.HTTP_201_CREATED
    return {"method": request.method}

#1.3
@app.get("/auth")
def check_pass(response: Response, password: str = Query(""), password_hash: str = Query("")):
    if password and password_hash:
        hashed = sha512(password.encode("utf-8")).hexdigest()
        if password_hash == hashed:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

#1.4
@app.post("/register")
async def new_patient(patient: Patient, response: Response):
    name_letters = "".join([item for item in patient.name if item.isalpha()])
    surname_letters = "".join([item for item in patient.surname if item.isalpha()])
    length = len(name_letters) + len(surname_letters)
    patient.vaccination_date = patient.register_date + timedelta(days=length)
    patient.id = app.counter
    app.storage[app.counter] = patient
    app.counter += 1
    response.status_code = status.HTTP_201_CREATED
    return patient

#1.5
@app.get("/patient/{id}")
def show_patient(id: int, response: Response):
    if id in app.storage:
        if id < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return app.storage.get(id)
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

#3.1
@app.get("/hello", response_class=HTMLResponse)
def get_hello(request: Request):
    current_date = datetime.now()
    str_date = current_date.strftime("%Y-%m-%d")
    return templates.TemplateResponse("index.html.j2", {
        "request": request, "message": f"Hello! Today date is {str_date}"})

#3.2
def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    '''Helper function for username/password check'''
    valid_username = secrets.compare_digest(credentials.username, "4dm1n")
    valid_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (valid_password and valid_username):
        status_code = 401
    else:
        status_code = 200
    return {"status_code": status_code,
            "valid_username": valid_username,
            "valid_password": valid_password}

@app.post("/login_session", status_code=201)
def login_session(response: Response, authorized: dict = Depends(check_credentials)):
    if authorized["status_code"] == 200:
        secret_key = secrets.token_hex(16)
        session_token = sha256(f'{authorized["valid_username"]}{authorized["valid_password"]}{secret_key}'.encode()).hexdigest()
        if len(app.session_cookie_tokens) >= 3:
            del app.session_cookie_tokens[0]
        app.session_cookie_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
    elif authorized["status_code"] == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"})
    return {"message": "Session established"}

@app.post("/login_token", status_code=201)
def login_token(authorized: dict = Depends(check_credentials)):
    if authorized["status_code"] == 200:
        secret_key = secrets.token_hex(16)
        token_value = sha256(f'{authorized["valid_username"]}{authorized["valid_password"]}{secret_key}'.encode()).hexdigest()
        if len(app.session_tokens) >= 3:
            del app.session_tokens[0]
        app.session_tokens.append(token_value)
    elif authorized["status_code"] == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"})
    return {"token": token_value}

#3.3
@app.get("/welcome_session")
def welcome_session(session_token: str = Cookie(None), is_format: Message = Depends(Message)):
    if not session_token or session_token not in app.session_cookie_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()

@app.get("/welcome_token")
def welcome_token(token: Optional[str] = Query(None), is_format: Message = Depends(Message)):
    if not token or token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()

#3.4
@app.delete("/logout_session")
def logout_session(session_token: str = Cookie(None), format: str = Query("")):
    if not session_token or session_token not in app.session_cookie_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        app.session_cookie_tokens.remove(session_token)
        url = f"/logged_out?format={format}"
        return RedirectResponse(url=url, status_code=303)

@app.delete("/logout_token")
def logout_token(token: Optional[str] = Query(None), format: str = Query("")):
    if not token or token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        app.session_tokens.remove(token)
        url = f"/logged_out?format={format}"
        return RedirectResponse(url=url, status_code=303)

@app.get("/logged_out")
def logged_out(is_format: Message = Depends(Message)):
    is_format.word = "Logged out"
    return is_format.return_message()
    
