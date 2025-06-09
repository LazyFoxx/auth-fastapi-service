from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.redis.redis_client_manager import RedisClient
from src.infrastructure.api.v1.routes.auth import router as auth_router
from src.infrastructure.email.email_client_manager import EmailClietn
from src.config import settings

app = FastAPI()
app.include_router(auth_router)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]



@app.on_event("startup")
async def on_startup():
    await RedisClient.connect()
    await EmailClietn.connect()


@app.on_event("shutdown")
async def on_shutdown():
    await RedisClient.disconnect()
    await EmailClietn.disconnect()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
