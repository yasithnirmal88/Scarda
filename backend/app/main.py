from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, sections, inverters, strings, alerts, weather, string_readings

app = FastAPI(title="Solar AIM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(sections.router, prefix="/api/sections", tags=["Sections"])
app.include_router(inverters.router, prefix="/api/inverters", tags=["Inverters"])
app.include_router(strings.router, prefix="/api/strings", tags=["Strings"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(string_readings.router, prefix="/api/string-readings", tags=["String Readings"])


@app.get("/")
def root():
    return {"message": "Solar AIM API"}
