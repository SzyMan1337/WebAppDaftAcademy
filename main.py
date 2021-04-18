from fastapi import FastAPI

app = FastAPI()

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

@app.post("/method")
def method_post():
    return {"method": "POST"}