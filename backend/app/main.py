from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.db import engine, Base
from app import models  # keep this import so tables register

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UrbanResQ API",
    description="Backend API for YDTC Flood & Extreme Heat Monitoring System",
    version="0.1.0"
)

# CORS fix (so frontend at localhost:5500 can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "running", "service": "UrbanResQ Backend"}
