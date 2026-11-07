from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="The Chocolate Factory Mini-MRP",
    description="Backend API for Chocolate Factory.",
    version="1.0.0",
)

# API routerlarni ulaymiz
app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")