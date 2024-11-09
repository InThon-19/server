
import os
from bson import ObjectId
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import uvicorn
from gcp_utils import resize_and_convert_to_webp
from datetime import datetime
from models import Comment, Post, Record
from models import db, user_collection, post_collection, record_collection
from gcp_utils import bucket
from typing import Dict


app = FastAPI(
    title="ABCD Api Server",
    description="This is the API server for ABCD project.",
)


def calculateRating(post):
    rating = sum(float(comment['Rating']) for comment in post.get(
        "Comments", [])) / (len(post.get("Comments", [])) or 1)
    return rating


def calculateSelfRating(post):
    rating = sum(float(record['SelfRating']) for record in post.get(
        "Records", [])) / (len(post.get("Records", [])) or 1)
    return rating


def transformPost(post):
    if "_id" in post:
        post["_id"] = str(post["_id"])
    return post

# @@ APIHandler ############################


@app.post("/api/img", tags=["API"])
async def upload_image(file: UploadFile = File(...), width: int = 800, height: int = 800):
    try:
        original_image = await file.read()
        webp_image = resize_and_convert_to_webp(original_image, width, height)
        filename = os.path.splitext(file.filename)[0]

        blob = bucket.blob(f"uploads/{filename}.webp")
        blob.upload_from_string(webp_image, content_type="image/webp")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Image uploaded successfully",
                "url": blob.public_url
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading image: {e}")


@app.get("/api/health", tags=["API"])
async def checkStatus():
    current_time = datetime.now()
    return JSONResponse(
        status_code=200,
        content={"status": "200", "status": "Server running",
                 "datetime": str(current_time)}
    )


@app.get("/api/user/{userId}", tags=["API"])
async def checkUserExists(userId: str):
    user = user_collection.find_one({"UserId": userId})
    if user:
        return {"data": {}}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/api/user/{userId}", tags=["API"])
async def registerUser(userId: str, request: Request):
    data = await request.json()

    existing_user = user_collection.find_one({"UserId": userId})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = {
        "UserId": userId,
        "Nickname": data.get("Nickname"),
        "Email": data.get("Email"),
        "ProfileImage": data.get("ProfileImage")
    }
    result = user_collection.insert_one(user_data)

    return {
        "data": {
            "_id": str(result.inserted_id),
            "UserId": userId,
            "Email": data.get("Email")
        }
    }

@app.get("/api/user/{userId}/rating", tags=["API"])
async def getUserRatings(userId: str, date: str = Query("day"), count: int = 30) -> Dict:
    if date == "day":
        # 일별 데이터: 최신순으로 게시물을 count 개수만큼 조회
        posts = post_collection.find({"UserId": userId}).sort("Date", -1).limit(count)
        data = [
            {
                "self_rating": calculateSelfRating(post),
                "comment_rating": calculateRating(post),
                "date": str(post["Date"].date())
            }
            for post in posts
        ]

    elif date == "month":
        # 월별 데이터: 연도와 월별로 그룹화하여 count 개수만큼 최신 데이터를 조회
        posts = post_collection.aggregate([
            {"$match": {"UserId": userId}},
            {"$group": {
                "_id": {"year": {"$year": "$Date"}, "month": {"$month": "$Date"}},
                "posts": {"$push": "$$ROOT"}
            }},
            {"$sort": {"_id.year": -1, "_id.month": -1}},
            {"$limit": count}
        ])

        data = [
            {
                "self_rating": sum(calculateSelfRating(post) for post in month["posts"]) / len(month["posts"]),
                "comment_rating": sum(calculateRating(post) for post in month["posts"]) / len(month["posts"]),
                "date": f"{month['_id']['year']}-{month['_id']['month']:02}"
            }
            for month in posts
        ]

    elif date == "year":
        # 연별 데이터: 연도로 그룹화하여 count 개수만큼 최신 데이터를 조회
        posts = post_collection.aggregate([
            {"$match": {"UserId": userId}},
            {"$group": {
                "_id": {"year": {"$year": "$Date"}},
                "posts": {"$push": "$$ROOT"}
            }},
            {"$sort": {"_id.year": -1}},
            {"$limit": count}
        ])

        data = [
            {
                "self_rating": sum(calculateSelfRating(post) for post in year["posts"]) / len(year["posts"]),
                "comment_rating": sum(calculateRating(post) for post in year["posts"]) / len(year["posts"]),
                "date": f"{year['_id']['year']}"
            }
            for year in posts
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid date parameter. Use 'day', 'month', or 'year'.")

    return {"data": data}


@app.get("/api/post", tags=["API"])
async def getCalendarPost(year: int, month: int, user_id: str):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year+1, 1, 1)
    else:
        end_date = datetime(year, month+1, 1)

    posts_in_month = post_collection.find({
        "Date": {
            "$gte": start_date,
            "$lt": end_date,
        }
    })

    data = []
    for post in posts_in_month:
        formatted_post = {
            "_id": str(post["_id"]),
            "UserId": user_id,
            "Records": post.get("Records", []),
            "Comments": post.get("Comments", []),
            "Visibility": post.get("Visibility", True),
            "Date": post["Date"],
            "Rating": calculateRating(post),
            "CommentsNum": len(post.get("Comments", [])),
            "SelfRating": calculateSelfRating(post),
        }

        data.append(formatted_post)

    return {"data": data}


@app.post("/api/record", tags=["API"])
async def postRecord(user_id: str, year: int, month: int, day: int, request: Request):
    """
    request
        When string
        Who string
        Where string
        What string
        How string
        Why string
        Image string
        SelfRating float
        Date Date
    """
    payload = await request.json()
    new_records = {
        "UserId": user_id,
        "When": payload.get("When"),
        "Who": payload.get("Who"),
        "Where": payload.get("Where"),
        "What": payload.get("What"),
        "How": payload.get("How"),
        "Why": payload.get("Why"),
        "Image": payload.get("Image"),
        "SelfRating": payload.get("SelfRating"),
        "Date": payload.get("Date"),
    }

    data = {
        "UserId": user_id,
        "Records": [new_records],
        "Comments": [],
        "Visibility": True,
        "Date": datetime.now()
    }

    exist_post = list(post_collection.find(
        {"UserId": user_id}).sort('Date', -1).limit(1))

    if len(exist_post) > 0:
        latest_date = exist_post[0]['Date']

        if latest_date.year == year and latest_date.month == month and latest_date.day == day:
            post_collection.update_one(
                {"_id": exist_post[0]["_id"]},
                {"$push": {"Records": new_records}}
            )
            return {"data": transformPost(exist_post[0])}

    post_collection.insert_one(data)
    return {"data": transformPost(data)}


@app.get("/api/post/feed", tags=["API"])
async def getFeed():
    latest_posts30 = list(post_collection.find().sort('Date', -1).limit(30))
    data = []
    for post in latest_posts30:
        user_info = user_collection.find_one({"UserId": post["UserId"]})

        is_yesterday = (datetime.now() - post['Date']).days == 1

        formatted_post = {
            "_id": post["_id"],
            "UserId": transformPost(user_info),
            "Records": post.get("Records", []),
            "Comments": post.get("Comments", []),
            "Visibility": post.get("Visibility", True),
            "Date": post["Date"] if is_yesterday else None,
            "Rating": calculateRating(post),
            "CommentsNum": len(post.get("Comments", [])),
            "SelfRating": calculateSelfRating(post),
        }

        data.append(transformPost(formatted_post))

    return {"data": data}


def to_object_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
