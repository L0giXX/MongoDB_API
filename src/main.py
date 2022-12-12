import pymongo
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from .data import DataHandler
from .auth import register_user, authenticate_user, create_access_token, get_current_active_user
from .models import RegModel, AuthModel, DataModel
from dotenv import dotenv_values

config = dotenv_values("src/.env")


client = pymongo.MongoClient(config["MONGODB_URL"])
db = client["ESP32DB"]
dataC = db["data"]
profileC = db["profile"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(req: RegModel):
    req = jsonable_encoder(req)
    req["password"] = register_user(profileC, req)
    newData = profileC.insert_one(req)
    curData = profileC.find_one({"_id": newData.inserted_id})
    return JSONResponse(status_code=status.HTTP_200_OK, content=curData)


@app.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        profileC, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token, "token_type": "bearer"})


@app.get("/user")
def read_users_me(current_user: AuthModel = Depends(get_current_active_user)):
    return Response(status_code=status.HTTP_200_OK, content=current_user)


@app.get("/profile/get")
def get_profile():
    tmp = []
    for x in profileC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.post("/data/add")
def add_data(req: DataModel):
    req = jsonable_encoder(req)
    data = DataHandler.add_data(dataC, req)
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
    dict = DataHandler.get_data(dataC, None, "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/temp/kitchen")
def get_temp():
    dict = {}
    dict = DataHandler.get_data(dataC, "Kitchen", "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/temp/bedroom")
def get_temp():
    dict = {}
    dict = DataHandler.get_data(dataC, "Bedroom", "BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi")
def get_humi():
    dict = {}
    dict = DataHandler.get_data(dataC, None, "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi/kitchen")
def get_humi():
    dict = {}
    dict = DataHandler.get_data(dataC, "Kitchen", "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi/bedroom")
def get_humi():
    dict = {}
    dict = DataHandler.get_data(dataC, "Bedroom", "BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press")
def get_press():
    dict = {}
    dict = DataHandler.get_data(dataC, None, "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press/kitchen")
def get_press():
    dict = {}
    dict = DataHandler.get_data(dataC, "Kitchen", "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press/bedroom")
def get_press():
    dict = {}
    dict = DataHandler.get_data(dataC, "Bedroom", "BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/power")
def get_power():
    dict = {}
    dict = DataHandler.get_data(dataC, None, "CT-Sensor", "power")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.delete("/data/delete")
def delete_data():
    x = dataC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")


@app.delete("/profile/delete")
def delete_data():
    x = profileC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")
