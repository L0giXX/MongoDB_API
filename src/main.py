import pymongo
import requests
from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from .data import add_air_data, add_power_data, get_data
from .auth import *
from .models import RegModel, AuthModel, DataAirModel, DataPowerModel

config = dotenv_values("src/.env")

client = pymongo.MongoClient(config["MONGODB_URL"])
db = client["ESP32DB"]
dataC = db["data"]
profileC = db["profile"]

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = config["API_KEY"]
CITY = "Vienna"

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius


def hpa_to_bar(hPA):
    bar = hPA/1000
    return bar


@app.get("/weather")
def get_weather():
    dict = {}
    response = requests.get(url)
    data = response.json()
    weather = data["weather"][0]["main"]
    temp_curr_celsius = round(kelvin_to_celsius(data["main"]["temp"]), 2)
    temp_max_celsius = round(kelvin_to_celsius(data["main"]["temp_max"]), 2)
    temp_min_celsius = round(kelvin_to_celsius(data["main"]["temp_min"]), 2)
    humi = data["main"]["humidity"]
    press_bar = hpa_to_bar(data["main"]["pressure"])

    dict.update({"Weather": weather, "Current_Temperature": temp_curr_celsius, "Max_Temperature": temp_max_celsius,
                 "Min_Temperature": temp_min_celsius, "Humidity": humi, "Pressure": press_bar})
    return JSONResponse(content=dict, status_code=status.HTTP_200_OK)


@app.post("/register")
def register(req: RegModel):
    req = jsonable_encoder(req)
    req["password"] = register_user(profileC, req)
    newData = profileC.insert_one(req)
    curData = profileC.find_one({"_id": newData.inserted_id})
    return JSONResponse(status_code=status.HTTP_200_OK, content=curData)


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(profileC, form_data.username, form_data.password)
    access_token = create_access_token(user)
    tmp = JSONResponse(status_code=status.HTTP_200_OK, content={
                       "access_token": access_token, "token_type": "bearer"})
    tmp.headers["Access-Control-Allow-Origin"] = "*"
    return tmp


@app.get("/user/me")
def read_users_me(current_user: AuthModel = Depends(get_current_active_user)):
    return Response(status_code=status.HTTP_200_OK, content=current_user)


@app.post("/user/password")
def password(req: AuthModel):
    tmp = []
    req = jsonable_encoder(req)
    tmp = change_password(profileC, req["username"], req["password"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.get("/profile/get")
def get_profile():
    tmp = []
    for x in profileC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.post("/data/air/add")
def add_data(req: DataAirModel):
    req = jsonable_encoder(req)
    data = add_air_data(dataC, req)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@app.post("/data/power/add")
def add_data(req: DataPowerModel):
    req = jsonable_encoder(req)
    data = add_power_data(dataC, req)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@app.get("/")
def root():
    return {"message": "Diplomarbeit"}


@app.get("/data/get")
def get_all_data():
    tmp = []
    for x in dataC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.get("/data/get/temp")
def get_temp():
    dict = {}
    dict = get_data(dataC, None, "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/temp/kitchen")
def get_temp():
    dict = {}
    dict = get_data(dataC, "Kitchen", "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/temp/bedroom")
def get_temp():
    dict = {}
    dict = get_data(dataC, "Bedroom", "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi")
def get_humi():
    dict = {}
    dict = get_data(dataC, None, "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi/kitchen")
def get_humi():
    dict = {}
    dict = get_data(dataC, "Kitchen", "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi/bedroom")
def get_humi():
    dict = {}
    dict = get_data(dataC, "Bedroom", "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press")
def get_press():
    dict = {}
    dict = get_data(dataC, None, "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press/kitchen")
def get_press():
    dict = {}
    dict = get_data(dataC, "Kitchen", "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press/bedroom")
def get_press():
    dict = {}
    dict = get_data(dataC, "Bedroom", "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/power")
def get_power():
    dict = {}
    dict = get_data(dataC, None, "CT-Sensor", "power")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.delete("/data/delete")
def delete_data():
    x = dataC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")


@app.delete("/profile/delete")
def delete_profile():
    x = profileC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")
