from fastapi import FastAPI
from app.routes.generate import router as generate_router

app = FastAPI(title="AI Service")

app.include_router(generate_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
