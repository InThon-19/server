
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from config import MONGO_URL

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




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


