from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from os import getenv
from .db import Base, engine
from .routers import auth, items, cart, health

# Create tables on startup (simple for this assignment)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(cart.router)
