from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Database
from .routers import github

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github.router)


@app.on_event("startup")
async def startup():
    db = await Database.create()


@app.get("/")
async def root():
    return {"message": "Hello world!"}
