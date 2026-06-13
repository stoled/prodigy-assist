from fastapi import FastAPI
from app.routes.generate import router as generate_router
from app.routes.health import router as health_router

app = FastAPI(title="AI Service")

app.include_router(generate_router)
app.include_router(health_router)
