from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory, ItemType
from app.schemas.inventory import InventoryCreate, RestockRequest

# PostgreSQL INTEGER ustunining maksimal qiymati
MAX_STOCK = 2_147_483_647


async def create_inventory_item(
    session: AsyncSession, request: InventoryCreate
) -> Inventory:
    try:
        async with session.begin():
            exists_stmt = select(Inventory.id).where(
                func.lower(Inventory.name) == request.name.lower()
            )
            exists_result = await session.execute(exists_stmt)

            if exists_result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"'{request.name}' nomli element omborda allaqachon mavjud.",
                )

            item = Inventory(**request.model_dump())
            session.add(item)
            await session.flush()
    except IntegrityError:
        # Parallel so'rov xuddi shu nomni bizdan oldin yozib ulgurgan holat
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{request.name}' nomli element omborda allaqachon mavjud.",
        )

    return item


async def restock_item(
    session: AsyncSession, item_id: int, request: RestockRequest
) -> Inventory:
    async with session.begin():
        stmt = select(Inventory).where(Inventory.id == item_id).with_for_update()
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Element (ID={item_id}) omborda topilmadi.",
            )

        if item.item_type != ItemType.RAW_MATERIAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Faqat xom ashyo (RAW_MATERIAL) to'ldiriladi. "
                    "Tayyor mahsulot /produce orqali ko'payadi."
                ),
            )

        if item.stock + request.quantity > MAX_STOCK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{item.name}' uchun qoldiq ruxsat etilgan chegaradan oshib ketadi.",
            )

        item.stock += request.quantity
        await session.flush()

    return item
