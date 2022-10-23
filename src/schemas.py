from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AuthModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    password: str
    email: EmailStr


class DataModel(BaseModel):
    # automatically creates a MongoDB id for every post request
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    loc: str  # Küche / Wohnzimmer / Haus
    sensor: str  # BME680 / CT-Sensor
    temp: float
    humi: float
    press: float
    power: float
    # automatically creates a timestamp for every post request
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
