from fastapi import FastAPI
from backend.app.api.routes import router as api_router

app = FastAPI(
    title = "UrbanResQ API",
    description = "Backend API for YDTC Flood & Extreme Heat Monitoring System",
    version = "0.1.0"
)

app.include_router(api_router, prefix ="/api")

@app.get("/")
def root():
    return {
      "status" : "running",
      "service" : "UrbanResQ Backend"
    }