import pymongo
from fastapi import FastAPI, status, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from .auth import AuthHandler
from .models import AuthModel, DataModel

url = "mongodb+srv://L0giX:21032004Mm@clusterdata.chvb5kd.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(url)
db = client["ESP32DB"]
dataC = db["data"]
profileC = db["profile"]

app = FastAPI()
auth_handler = AuthHandler()


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
    if profileC.find_one({"username": req["username"]}):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Username bereits benutzt: [" + req["username"]+"]")
    hashed_password = auth_handler.get_password_hash(req["password"])
    req["password"] = hashed_password
    newData = profileC.insert_one(req)
    curData = profileC.find_one({"_id": newData.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=curData)


@app.post("/login")
def login(req: AuthModel):
    tmp = []
    user: str
    token: str
    req = jsonable_encoder(req)
    # Authenticate user and verify password
    if profileC.find_one({"username": req["username"]}):
        user = req["username"]
        for x in profileC.find({"username": user}):
            tmp.append(x)
        if auth_handler.verify_password(req["password"], tmp[0]["password"]):
            token = auth_handler.encode_token(user, "access")
            return Response(status_code=status.HTTP_201_CREATED, content="Token: "+token)
        else:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Passwort nicht korrekt!")
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Username nicht registriert!")


@app.get('/unprotected')
def unprotected():
    return {'hello': 'world'}


@app.get("/protected")
def protected(username=Depends(auth_handler.auth_wrapper)):
    return Response(status_code=status.HTTP_200_OK, content="Name: "+username)


@app.get("/profile/get")
def getProfile():
    tmp = []
    for x in profileC.find():
        tmp.append(x)
    return JSONResponse(status_code=status.HTTP_200_OK, content=tmp)


@app.post("/data/add")
def addData(req: DataModel):
    req = jsonable_encoder(req)
    if req["sensor"] == "BME680":
        req.pop("power")    # delete key: power
        if req["temp"] < -20 or req["temp"] > 50:
            return Response(content="Keine normalen Temperaturen gemessen: [" + str(req["temp"])+"]")

        elif req["humi"] < 40 or req["humi"] > 70:
            return Response(content="Keine normale Luftfeuchtigkeit gemessen: [" + str(req["humi"])+"]")

        elif req["press"] < 900 or req["press"] > 1100:
            return Response(content="Keinen normalen Druck gemessen: [" + str(req["press"])+"]")

        else:
            newData = dataC.insert_one(req)
            curData = dataC.find_one({"_id": newData.inserted_id})
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=curData)

    elif req["sensor"] == "CT-Sensor":
        req.pop("temp")     # delete key: temp
        req.pop("humi")     # delete key: humi
        req.pop("press")    # delete key: press
        newData = dataC.insert_one(req)
        curData = dataC.find_one({"_id": newData.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=curData)
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


@app.get("/data/get/latest")
def getlatestData():
    tmp = []
    for x in dataC.find():
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
