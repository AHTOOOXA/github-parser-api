from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Database
# from app.api.routers import api_routers
from app.api.routers import api_routers

app = FastAPI(
    title="API for Github parser",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in api_routers:
    app.include_router(router)


@app.on_event("startup")
async def startup():
    db = await Database.create()


@app.get("/")
async def root():
    return {"message": "Hello world!"}
