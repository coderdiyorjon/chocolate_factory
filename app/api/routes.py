from fastapi import APIRouter, Depends, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.inventory import Inventory, ProductionLog, Recipe
from app.schemas.inventory import (InventoryCreate, InventoryResponse,
                                   ProduceRequest, ProduceResponse,
                                   ProductionLogResponse, RecipeCreate,
                                   RecipeResponse, RestockRequest)
from app.services.inventory import create_inventory_item, restock_item
from app.services.production import produce_product
from app.services.recipe import create_recipe

router = APIRouter()


@router.get(
    "/inventory",
    response_model=list[InventoryResponse],
    summary="Residue in an inventory",
)
async def get_inventory(session: AsyncSession = Depends(get_db)):
    stmt = select(Inventory).order_by(Inventory.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/inventory",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adding a new item to the inventory",
)
async def add_inventory_item(
    request: InventoryCreate, session: AsyncSession = Depends(get_db)
):
    return await create_inventory_item(session, request)


@router.post(
    "/inventory/{item_id}/restock",
    response_model=InventoryResponse,
    summary="Restocking a raw material",
)
async def restock(
    request: RestockRequest,
    item_id: int = Path(gt=0, description="ID of the RAW_MATERIAL"),
    session: AsyncSession = Depends(get_db),
):
    return await restock_item(session, item_id, request)


@router.get(
    "/recipes",
    response_model=list[RecipeResponse],
    summary="List of recipes",
)
async def get_recipes(session: AsyncSession = Depends(get_db)):
    stmt = select(Recipe).order_by(Recipe.product_id, Recipe.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/recipes",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adding a material to a product recipe",
)
async def add_recipe(
    request: RecipeCreate, session: AsyncSession = Depends(get_db)
):
    return await create_recipe(session, request)


@router.post(
    "/produce",
    response_model=ProduceResponse,
    summary="Producing a product",
)
async def produce(
    request: ProduceRequest, session: AsyncSession = Depends(get_db)
):
    return await produce_product(session, request)


@router.get(
    "/production-logs",
    response_model=list[ProductionLogResponse],
    summary="History of production",
)
async def get_production_logs(session: AsyncSession = Depends(get_db)):
    stmt = select(ProductionLog).order_by(ProductionLog.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
