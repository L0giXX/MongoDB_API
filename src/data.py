import re
import pymongo
from fastapi import HTTPException


def max(db, loc, sensor, type, dict):
    tmp = []
    if loc == None:
        for x in db.find({"sensor": sensor}).sort(type, pymongo.DESCENDING).limit(1):
            tmp.append(x)
    else:
        for x in db.find({"loc": loc, "sensor": sensor}).sort(type, pymongo.DESCENDING).limit(1):
            tmp.append(x)
    max = round(tmp[0][type], 2)
    dict.update({"Max": max})


def min(db, loc, sensor, type, dict):
    tmp = []
    if loc == None:
        for x in db.find({"sensor": sensor}).sort(type, pymongo.ASCENDING).limit(1):
            tmp.append(x)
    else:
        for x in db.find({"loc": loc, "sensor": sensor}).sort(type, pymongo.ASCENDING).limit(1):
            tmp.append(x)
    min = round(tmp[0][type], 2)
    dict.update({"Min": min})


def average(db, loc, sensor, type, dict):
    tmp = []
    sum = 0
    count = 0
    if loc == None:
        for x in db.find({"sensor": sensor}):
            tmp.append(x)
    else:
        for x in db.find({"loc": loc, "sensor": sensor}):
            tmp.append(x)
    while (count < len(tmp)):
        help = tmp[count][type]
        sum += help
        count += 1
    avg = round(sum/len(tmp), 2)
    dict.update({"Avg": avg})


def current(db, loc, sensor, type, dict):
    tmp = []
    if loc == None:
        for x in db.find({"sensor": sensor}):
            tmp.append(x)
    else:
        for x in db.find({"loc": loc, "sensor": sensor}):
            tmp.append(x)
    current = tmp[-1][type]
    dict.update({"Current": current})

    # Hilfsfunktion um Sensor Daten in Datenbank speichern


def add_air_data(db, data):
    if re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", data["ip"]):
        if data["sensor"] == "BME680":

            data["temp"] = round(data["temp"], 2)
            data["humi"] = round(data["humi"], 2)
            data["press"] = round(data["press"], 2)

            if data["temp"] < -20 or data["temp"] > 50:
                raise HTTPException(
                    status_code=400, detail="Wrong temperature input")

            elif data["humi"] < 20 or data["humi"] > 90:
                raise HTTPException(
                    status_code=400, detail="Wrong humidity input")

            elif data["press"] < 0 or data["press"] > 1.5:
                raise HTTPException(
                    status_code=400, detail="Wrong pressure input")

            else:
                newData = db.insert_one(data)
                curData = db.find_one({"_id": newData.inserted_id})
                return curData
        else:
            raise HTTPException(
                status_code=400, detail="Wrong sensor in use")
    else:
        raise HTTPException(status_code=400, detail="Wrong IP adress")


def add_power_data(db, data):
    if re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", data["ip"]):
        if data["sensor"] == "CT-Sensor":
            data["power"] = round(data["power"], 2)
            newData = db.insert_one(data)
            curData = db.find_one({"_id": newData.inserted_id})
            return curData
        else:
            raise HTTPException(
                status_code=400, detail="Wrong sensor in use")
    else:
        raise HTTPException(status_code=400, detail="Wrong IP adress")

    # Hilfsfunkion um Max, Min, Average, Current (ggf. Location Eingabe) Wert zu erhalten


def get_data(db, loc, sensor, type):
    dict = {}
    if not db.find_one({"loc": loc}) and loc != None:
        raise HTTPException(
            status_code=400, detail="No entries for this location")
    max(db, loc, sensor, type, dict)
    min(db, loc, sensor, type, dict)
    average(db, loc, sensor, type, dict)
    current(db, loc, sensor, type, dict)
    return dict
