from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import (InventoryResponse, ProduceRequest,
                                   ProduceResponse)
from app.services.production import produce_product

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
    "/produce",
    response_model=ProduceResponse,
    summary="Producing a product",
)
async def produce(
    request: ProduceRequest, session: AsyncSession = Depends(get_db)
):
    return await produce_product(session, request)