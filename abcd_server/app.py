
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import uvicorn
import models
from datetime import datetime
from abcd_server.models import Comment, Post, Record
from models import db

app = FastAPI(
    title="ABCD Api Server",
    description="This is the API server for ABCD project.",
)


def calculateRating(post):
    rating = sum(comment['rating'] for comment in post.get(
        "Comments", [])) / (len(post.get("Comments", [])) or 1)
    return rating


def calculateSelfRating(post):
    rating = sum(record['self_rating'] for record in post.get(
        "Records", [])) / (len(post.get("Records", [])) or 1)
    return rating

# @@ APIHandler ############################


@app.get("/api/health", tags=["API"])
async def checkStatus():
    current_time = datetime.now()
    return JSONResponse(
        status_code=200,
        content={"status": "200", "status": "Server running",
                 "datetime": str(current_time)}
    )


@app.get("/api/post/feed", tags=["API"])
async def getFeed():
    latest_posts30 = db['post'].find().sort('_id', -1).limit(30)
    data = []
    for post in latest_posts30:
        user_info = db['user'].find_one({"_id": post["UserId"]})

        is_yesterday = (datetime.now() - post['date']).days == 1

        formatted_post = {
            "_id": str(post["_id"]),
            "UserId": user_info,
            "Records": post.get("Records", []),
            "Comments": post.get("Comments", []),
            "Visibility": post.get("Visibility", True),
            "Date": post["Date"] if is_yesterday else None,
            "Rating": calculateRating(post),
            "CommentsNum": len(post.get("Comments", [])),
            "SelfRating": calculateSelfRating(post),
        }

        data.append(formatted_post)

    return {"data": data}


def to_object_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
