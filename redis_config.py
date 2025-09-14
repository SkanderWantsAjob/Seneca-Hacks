import redis.asyncio as redis
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Using async Redis for FastAPI
# Connection pool allows multiple clients to share a connection
redis_pool: Optional[redis.Redis] = None

async def get_redis_pool() -> redis.Redis:
    """Initializes and returns the Redis connection pool."""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True # Decodes responses to strings
        )
    return redis_pool

async def close_redis_pool():
    """Closes the Redis connection pool."""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: initialize Redis pool
    print("Initializing Redis connection pool...")
    await get_redis_pool()
    yield
    # Shutdown event: close Redis pool
    print("Closing Redis connection pool...")
    await close_redis_pool()