import requests_cache
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from retry_requests import retry
import openmeteo_requests
from fastapi.middleware.cors import CORSMiddleware



# Konfiguracja klienta API Open-Meteo z cache i ponowieniami prób w przypadku błędu
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

app = FastAPI()

origins = [
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/", tags=["ROOT"])
async def root() -> dict:
    return {"status": "OK"}

class WeatherResponse(BaseModel):
    date: List[str]
    max_temperature: List[float]
    min_temperature: List[float]
    daylight_duration: List[float]

class EnergyResponse(BaseModel):
    day: int
    daylight_exposure: float
    energy_generated: float

@app.get("/weather", response_model=List[WeatherResponse])
async def get_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code", "sunrise", "sunset", "daylight_duration"],
        "forecast_days": 7
    }
    responses = openmeteo.weather_api(url, params=params)
    weather_data = []

    for response in responses:
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(5).ValuesAsNumpy()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ).astype(str).tolist(),
            "max_temperature": daily_temperature_2m_max.tolist(),
            "min_temperature": daily_temperature_2m_min.tolist(),
            "daylight_duration": daily_daylight_duration.tolist()
        }
        weather_data.append(daily_data)

    return weather_data

@app.get("/energy", response_model=List[EnergyResponse])
async def get_energy(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code", "sunrise", "sunset", "daylight_duration"],
        "forecast_days": 7
    }
    responses = openmeteo.weather_api(url, params=params)
    energy_data = []

    for i, response in enumerate(responses):
        daily = response.Daily()
        daily_daylight_duration = daily.Variables(5).ValuesAsNumpy()

        def calculate_generated_energy(daylight_duration):
            solar_power_output = 2.5  # Moc instalacji fotowoltaicznej w kW
            panel_efficiency = 0.2  # Efektywność paneli
            energy_generated = solar_power_output * daylight_duration * panel_efficiency
            return energy_generated

        for i in range(len(daily_daylight_duration)): # Poprawka tutaj
            generated_energy = calculate_generated_energy(daily_daylight_duration[i])
            energy_data.append({
                "day": i + 1,
                "daylight_exposure": daily_daylight_duration[i],
                "energy_generated": generated_energy
            })

    return energy_data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)