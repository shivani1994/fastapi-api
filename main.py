import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.products import router as products_routers

app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(products_routers)

@app.get("/")
def test_func():
    return "Hi,Welcome to FastAPI" 

