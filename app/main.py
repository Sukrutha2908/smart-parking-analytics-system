from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import parking
from app.routers import analytics

app = FastAPI(
    title="Smart Parking Analytics System"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(parking.router)
app.include_router(analytics.router)

@app.get("/")
def home():
    return {
        "message": "Smart Parking API Running"
    }

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('app/static/favicon.ico')