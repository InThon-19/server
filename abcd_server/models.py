from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from config import MONGO_URL, DB_NAME

# Custom ObjectId for Pydantic v2 compatibility


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

# User model


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(alias="UserId")  # Unique identifier for reference
    email: str = Field(alias="Email")
    nickname: str = Field(alias="Nickname")
    profile_image: Optional[str] = Field(alias="ProfileImage")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Record model


class Record(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(alias="UserId")
    when: str = Field(alias="When")
    who: str = Field(alias="Who")
    where: str = Field(alias="Where")
    what: str = Field(alias="What")
    how: str = Field(alias="How")
    why: str = Field(alias="Why")
    image: Optional[str] = Field(alias="Image")
    date: datetime = Field(alias="Date")
    self_rating: float = Field(default=0.0, alias="SelfRating")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Comment model


class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(alias="UserId")
    rating: Optional[float] = Field(default=0.0, alias="Rating")
    body: str = Field(alias="Body")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Post model


class Post(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(alias="UserId")
    records: List[Record] = Field(default=[], alias="Records")
    comments: List[Comment] = Field(default=[], alias="Comments")
    visibility: bool = Field(default=True, alias="Visibility")
    date: datetime = Field(alias="Date")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


client = MongoClient(MONGO_URL)
db = client[DB_NAME]
# user_collection = db["user"]
# post_collection = db["post"]
record_collection = db["record"]
comment_collection = db["comment"]
user_collection = db["user1"]
post_collection = db["post1"]