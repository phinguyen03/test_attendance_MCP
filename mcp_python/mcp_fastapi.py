from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os


DB_FILE = "attendance_db.json"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to Copilot domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Attendance(BaseModel):
    name: str
    email: str
    attendance_date: str
    status: str



def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return [
        {"name": "Jack", "email": "jack@gmail.com", "attendance_date": "8/20/2025", "status": "Present"},
        {"name": "Bob", "email": "bob@gmail.com", "attendance_date": "8/20/2025", "status": "Absent"},
        {"name": "Charlie", "email": "charlie@gmail.com", "attendance_date": "8/20/2025", "status": "Present"}
    ]

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Attendance API"}

@app.get("/employee", response_model=List[Attendance], response_class=JSONResponse)
def list_employee():
    return db
    
# --- GET Endpoint: Fetch single employee ---

@app.get("/employee/{employee_name}", response_model=Attendance, response_class=JSONResponse)
def read_employee(employee_name: str):
    for employee in db:
        if employee["name"] == employee_name:
            return employee
    raise HTTPException(status_code=404, detail="Employee not found")

@app.post("/employee/{employee_name}/{status}", response_model=Attendance, response_class=JSONResponse)
def update_employee_status(employee_name: str, status: str):
    for employee in db:
        if employee["name"] == employee_name:
            employee["status"] = status  # Directly update status
            save_db()  # Save changes to file
            return employee
    raise HTTPException(status_code=404, detail="Employee not found")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="Attendance API for MCP integration",
        routes=app.routes,
    )
    # Force spec version to 3.0.0 instead of 3.1.0
    openapi_schema["openapi"] = "3.0.0"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


