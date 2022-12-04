import pymongo
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from .auth import AuthHandler
from .models import AuthModel, DataModel, Token
from dotenv import dotenv_values
from .oauth2 import authenticate_user, create_access_token, get_current_active_user

config = dotenv_values("src/.env")


client = pymongo.MongoClient(config["MONGODB_URL"])
db = client["ESP32DB"]
dataC = db["data"]
profileC = db["profile"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)
Auth_Handler = AuthHandler()


class DataHandler():
    def getData(sensor, type):
        dict = {}
        tmp1 = []
        for x in dataC.find({"sensor": sensor}).sort(type, pymongo.DESCENDING).limit(1):
            tmp1.append(x)
        max = round(tmp1[0][type], 2)

        tmp2 = []
        for x in dataC.find({"sensor": sensor}).sort(type, pymongo.ASCENDING).limit(1):
            tmp2.append(x)
        min = round(tmp2[0][type], 2)

        tmp3 = []
        summe = 0
        i = 0
        for x in dataC.find({"sensor": sensor}):
            tmp3.append(x)
        while (i < len(tmp3)):
            hilfe = tmp3[i][type]
            summe += hilfe
            i += 1
        avg = round(summe/len(tmp3), 2)

        dict.update({"Max": max})
        dict.update({"Min": min})
        dict.update({"Avg": avg})
        return dict


@app.post("/register")
def register(req: AuthModel):
    req = jsonable_encoder(req)
    req["password"] = Auth_Handler.authenticate_user(
        profileC, req["username"], req["password"])
    newData = profileC.insert_one(req)
    curData = profileC.find_one({"_id": newData.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=curData)


@app.post("/login")
def login(req: AuthModel):
    req = jsonable_encoder(req)
    tmp = []
    token: str
    tmp = Auth_Handler.get_user(profileC, req["username"])
    if Auth_Handler.verify_password(req["password"], tmp[0]["password"]):
        token = Auth_Handler.encode_token(tmp[0]["username"])
        return Response(status_code=status.HTTP_201_CREATED, content="Token: "+token)
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Passwort nicht korrekt!")


@app.post("/token")
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user", response_model=AuthModel)
async def read_users_me(current_user: AuthModel = Depends(get_current_active_user)):
    return current_user


@app.get('/unprotected')
def unprotected():
    return {'hello': 'world'}


@app.get("/protected")
def protected(current_user: AuthModel = Depends(Auth_Handler.auth_wrapper)):
    return Response(status_code=status.HTTP_200_OK, content="Benutzer: "+current_user)


@app.get("/profile/get")
def getProfile(request=Depends(Auth_Handler.auth_wrapper)):
    tmp = []
    for x in profileC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.post("/data/add")
def addData(req: DataModel):
    req = jsonable_encoder(req)
    if req["sensor"] == "BME680":
        req["temp"] = round(req["temp"], 2)
        req["humi"] = round(req["humi"], 2)
        req["press"] = round(req["press"], 2)
        req.pop("power")
        if req["temp"] < -20 or req["temp"] > 50:
            return Response(content="Keine normalen Temperaturen gemessen: [" + str(req["temp"])+"]")

        elif req["humi"] < 20 or req["humi"] > 70:
            return Response(content="Keine normale Luftfeuchtigkeit gemessen: [" + str(req["humi"])+"]")

        elif req["press"] < 0 or req["press"] > 1.5:
            return Response(content="Keinen normalen Druck gemessen: [" + str(req["press"])+"]")

        else:
            newData = dataC.insert_one(req)
            curData = dataC.find_one({"_id": newData.inserted_id})
            return JSONResponse(status_code=201, content=curData)

    elif req["sensor"] == "CT-Sensor":
        req["power"] = round(req["power"], 2)
        req.pop("temp")
        req.pop("humi")
        req.pop("press")
        newData = dataC.insert_one(req)
        curData = dataC.find_one({"_id": newData.inserted_id})
        return JSONResponse(status_code=201, content=curData)
    else:
        return Response(content="Falscher Sensor! ["+req["sensor"])


@app.get("/")
def root():
    return {"message": "Diplomarbeit"}


@app.get("/data/get")
def getallData():
    tmp = []
    for x in dataC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.get("/data/get/latest/air")
def getlatestData():
    tmp = []
    for x in dataC.find({"sensor": "BME680"}):
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp[-1])


@app.get("/data/get/latest/power")
def getlatestData():
    tmp = []
    for x in dataC.find({"sensor": "CT-Sensor"}):
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp[-1])


@app.get("/data/get/temp")
def getTemp():
    dict = {}
    dict = DataHandler.getData("BME680", "temp")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/humi")
def getPress():
    dict = {}
    dict = DataHandler.getData("BME680", "humi")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/press")
def getPress():
    dict = {}
    dict = DataHandler.getData("BME680", "press")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.get("/data/get/power")
def getPower():
    dict = {}
    dict = DataHandler.getData("CT-Sensor", "power")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict)


@app.delete("/data/delete")
def deleteData():
    x = dataC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")


@app.delete("/profile/delete")
def deleteData():
    x = profileC.delete_many({})
    return Response(content=str(x.deleted_count)+" Dokumente gelöscht")
