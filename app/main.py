from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    users,
    auth,
    lots,
    bids
)

app = FastAPI(
    title="auction API",
    description="online auction api",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(lots.router)
app.include_router(bids.router)

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "welcome to the auction API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
