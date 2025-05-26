from fastapi import FastAPI, Path, HTTPException, Query, responses
from typing import Optional, Annotated, Literal
from pydantic import BaseModel, Field, field_validator, computed_field
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient.", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient.", examples=["Ananya Sharma"])]
    city: Annotated[str, Field(..., description="City of the patient.", examples=["Guwahati"])]
    age: Annotated[int, Field(..., gt=0, le=120, description="Age of the patient.", examples=[28])]
    gender: Annotated[Literal["male", "female"], Field(..., description="Gender of the patient.", examples=["female"])]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in metres.", examples=[1.65])]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kilograms.", examples=[90.0])]

    @field_validator("name", "city")
    @classmethod
    def transform_name(cls, value):
        names = value.split(" ")
        return " ".join([name.capitalize() for name in names])
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(x):
    data = load_data()
    data.append(x)
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

def expand_query(query):
    if query in ["h", "height"]:
        return "height"
    elif query in ["w", "weight"]:
        return "weight"
    elif query in ["b", "bmi"]:
        return "bmi"
    elif query in ["a", "age"]:
        return "age"
    else:
        return query
    
def expand_order(order):
    if order in ["a", "asc"]:
        return "asc"
    elif order in ["d", "desc"]:
        return "desc"
    else:
        return order

def find_patient(data, patient_id):
    for i in data:
        if i["id"] == patient_id:
            return True
    return False

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return responses.RedirectResponse(url="/docs")

@app.get("/about", include_in_schema=False)
def about():
    return {"message": "A fully fledged Patient Management Syatem API to manage your patients"}


@app.get("/view")
def view(
    s: Optional[str] = Query(None, description="Sort by: height, weight, bmi, age or h, w, b, a"),
    o: Optional[str] = Query("asc", description="Sort order: asc, desc, a, d"),
):
    data = load_data()
    sort_by = s
    order = o

    if sort_by:
        valid_sort_by = ["height", "weight", "bmi", "age", "h", "w", "b", "a"]
        if sort_by not in valid_sort_by:
            raise HTTPException(status_code=400, detail="Invalid sort_by parameter")

        valid_order = ["asc", "desc", "a", "d"]
        if order not in valid_order:
            raise HTTPException(status_code=400, detail="Invalid order parameter")

        # Normalize
        sort_by = expand_query(sort_by)
        order = expand_order(order)

        # Sort
        data = sorted(data, key=lambda x: x[sort_by], reverse=(order == "desc"))

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient.", example="P001")):
    data = load_data()
    id_int = int(patient_id[1:])
    if patient_id in data:
        return data[id_int - 1]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()

    if find_patient(data, patient.id):
        raise HTTPException(status_code=400, detail="Patient already exists")

    x = patient.model_dump()

    save_data(x)

    return responses.JSONResponse(content={"message": "Patient created successfully"}, status_code=201)