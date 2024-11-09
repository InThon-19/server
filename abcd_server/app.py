
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import uvicorn
from datetime import datetime
from abcd_server.models import Comment, Post, Record
from models import db

app = FastAPI(
    title="ABCD Api Server",
    description="This is the API server for ABCD project.",
)


# @@ APIHandler ############################
@app.get("/api/health", tags=["API"])
async def checkStatus():
    current_time = datetime.now()
    return JSONResponse(
        status_code=200,
        content={"status": "200", "status": "Server running", "datetime": str(current_time)}
    )

# MongoDB connection setup
client = MongoClient("mongodb+srv://inthon2024:inthon2024@cluster0.ein72.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client[""]
post_collection = db["posts"]

# Convert BSON ObjectId to string for JSON responses
def to_object_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


