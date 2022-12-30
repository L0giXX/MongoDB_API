import pymongo
from fastapi import HTTPException


class DataHandler():
    # Hilfsfunktion um Sensor Daten in Datenbank speichern
    def add_air_data(db, data):
        x: str = data["ip"]
        if x.count('.') == 3:
            if data["sensor"] == "BME680":

                data["temp"] = round(data["temp"], 2)
                data["humi"] = round(data["humi"], 2)
                data["press"] = round(data["press"], 2)

                if data["temp"] < -20 or data["temp"] > 50:
                    raise HTTPException(
                        status_code=400, detail="Wrong temperature input")

                elif data["humi"] < 20 or data["humi"] > 70:
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
        x: str = data["ip"]
        if x.count('.') == 3:
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
        tmp1 = []
        tmp2 = []
        tmp3 = []
        tmp4 = []
        sum = 0
        count = 0

        if not db.find_one({"loc": loc}) and loc != None:
            raise HTTPException(
                status_code=400, detail="No entries for this location")

        # Max
        if loc == None:
            for x in db.find({"sensor": sensor}).sort(type, pymongo.DESCENDING).limit(1):
                tmp1.append(x)
        else:
            for x in db.find({"loc": loc, "sensor": sensor}).sort(type, pymongo.DESCENDING).limit(1):
                tmp1.append(x)
        max = round(tmp1[0][type], 2)
        dict.update({"Max": max})

        # Min
        if loc == None:
            for x in db.find({"sensor": sensor}).sort(type, pymongo.ASCENDING).limit(1):
                tmp2.append(x)
        else:
            for x in db.find({"loc": loc, "sensor": sensor}).sort(type, pymongo.ASCENDING).limit(1):
                tmp2.append(x)
        min = round(tmp2[0][type], 2)
        dict.update({"Min": min})

        # Average
        if loc == None:
            for x in db.find({"sensor": sensor}):
                tmp3.append(x)
        else:
            for x in db.find({"loc": loc, "sensor": sensor}):
                tmp3.append(x)
        while (count < len(tmp3)):
            help = tmp3[count][type]
            sum += help
            count += 1
        avg = round(sum/len(tmp3), 2)
        dict.update({"Avg": avg})

        # Latest
        if loc == None:
            for x in db.find({"sensor": sensor}):
                tmp4.append(x)
        else:
            for x in db.find({"loc": loc, "sensor": sensor}):
                tmp4.append(x)
        current = tmp4[-1][type]
        dict.update({"Current": current})

        return dict
