from fastapi import FastAPI
from .routes import api

app = FastAPI(
    title="This is basic CRUD operation Task with Authentication & Authorization",
)

app.include_router(api.router)
