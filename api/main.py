from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Smart Parking Analytics API Running"}