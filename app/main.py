import uvicorn as uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse

app = FastAPI()





@app.post("/calculate")
def calculate(num1: int = Form(ge=0, lt=111), num2: int = Form(ge=0, lt=111)):
    print("num1 =", num1, "   num2 =", num2)
    return {"result": num1 + num2}


@app.get("/calculate", response_class=FileResponse)
def calc_form():
    return "index.html"