from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

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

@app.get("/")
def hello():
    return {"message": "Patient Management Syatem API"}

@app.get("/about")
def about():
    return {"message": "A fully fledged Patient Management Syatem API to manage your patients"}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/view/sort")
def sort_patients(sort_by: str = Query(..., description="Sort on the basis of height, weight, bmi or age", example="height, b"), order: str = Query(..., description="Sort in ascending or descending order", example="asc, d")):
    valid_sort_by = ["height", "weight", "bmi", "age", "h", "w", "b", "a"]

    if(sort_by not in valid_sort_by):
        raise HTTPException(status_code=400, detail="Invalid sort_by parameter")

    valid_order = ["asc", "desc", "a", "d"]

    if(order not in valid_order):
        raise HTTPException(status_code=400, detail="Invalid order parameter")
    
    sort_by = expand_query(sort_by)
    order = expand_order(order)

    data = load_data()
    sorted_data = sorted(data.items(), key=lambda x: x[1][sort_by], reverse=(order == "desc"))
    return dict(sorted_data)

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient.", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")