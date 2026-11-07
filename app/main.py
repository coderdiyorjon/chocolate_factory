from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.db.init_db import create_tables, seed_data
from app.db.session import AsyncSessionLocal, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables and seed initial data on startup (idempotent).
    await create_tables()
    async with AsyncSessionLocal() as session:
        await seed_data(session)
    yield
    await engine.dispose()


app = FastAPI(
    title="The Chocolate Factory Mini-MRP",
    description="Backend API for Chocolate Factory.",
    version="1.0.0",
    lifespan=lifespan,
)

# API routerlarni ulaymiz
app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
