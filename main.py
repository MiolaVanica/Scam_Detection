from fastapi import FastAPI, HTTPException
from redis.asyncio import Redis
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Initialize Redis with Upstash credentials
redis = Redis.from_url(os.getenv("UPSTASH_REDIS_URL"), decode_responses=True)

class UIDCheckRequest(BaseModel):
    uids: list[str]

@app.post("/check-reselling-scam")
async def check_reselling_scam(request: UIDCheckRequest):
    """
    Check if any UIDs in the provided list exist in the Redis sold_uids set.
    Returns a list of UIDs that are found (indicating a reselling scam).
    """
    try:
        tasks = [redis.exists(f"uid:{uid}") for uid in request.uids]
        results = await asyncio.gather(*tasks)

        resold_uids = [uid for uid, exists in zip(request.uids, results) if exists]
        return {"resold_uids": resold_uids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking UIDs: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
