from fastapi import FastAPI
from app.api.routes import router as base_router
from app.api.risk import router as risk_router

app = FastAPI(
    title="UrbanResQ API",
    description="Backend API for YDTC Flood & Extreme Heat Monitoring System",
    version="0.1.0"
)

app.include_router(base_router, prefix="/api")
app.include_router(risk_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "running", "service": "UrbanResQ Backend"}
