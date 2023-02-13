from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from bson import ObjectId


class PyObjectId(ObjectId):
    # class for MongoDB ID
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


class RegModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    name: str
    surname: str
    email: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AuthModel(BaseModel):
    username: str
    password: str


class DataAirModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ip: str
    loc: str
    sensor: str
    temp: float
    humi: float
    press: float
    timestamp: datetime = Field(default_factory=lambda: (
        datetime.utcnow()+timedelta(hours=1)))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DataPowerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ip: str
    sensor: str
    power: float
    timestamp: datetime = Field(default_factory=lambda: (
        datetime.utcnow()+timedelta(hours=1)))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
