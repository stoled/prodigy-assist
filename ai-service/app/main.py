from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes.generate import router as generate_router
from app.routes.health import router as health_router
from app.routes.embeddings import router as embeddings_router
from app.services.db import get_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="AI Service", lifespan=lifespan)

app.include_router(generate_router)
app.include_router(health_router)
app.include_router(embeddings_router)
