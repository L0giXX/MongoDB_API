import pymongo
from fastapi import HTTPException


class DataHandler():
    # Hilfsfunkion um Max, Min, Average, Latest (ggf. Location Eingabe) Wert zu erhalten
    def get_data(db, loc, sensor, type):
        dict = {}
        tmp1 = []
        tmp2 = []
        tmp3 = []
        tmp4 = []
        sum = 0
        count = 0

        if not db.find_one({"loc": loc}):
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
        dict.update({"Latest": tmp4[-1][type]})

        return dict
