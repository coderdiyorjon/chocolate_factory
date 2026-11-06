from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory, ItemType, ProductionLog, Recipe
from app.schemas.inventory import (InventoryResponse, ProduceRequest,
                                   ProduceResponse, ProductionLogResponse)


async def produce_product(
    session: AsyncSession, request: ProduceRequest
) -> ProduceResponse:
    async with session.begin():
        recipe_stmt = select(Recipe).where(Recipe.product_id == request.product_id)
        recipe_result = await session.execute(recipe_stmt)
        recipes = list(recipe_result.scalars().all())

        if not recipes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mahsulot (ID={request.product_id}) uchun retsept topilmadi.",
            )

        item_ids = {request.product_id} | {r.material_id for r in recipes}

        lock_stmt = (
            select(Inventory)
            .where(Inventory.id.in_(item_ids))
            .order_by(Inventory.id)
            .with_for_update()
        )
        inv_result = await session.execute(lock_stmt)
        inventory_map: dict[int, Inventory] = {
            item.id: item for item in inv_result.scalars().all()
        }

        product = inventory_map.get(request.product_id)
        if not product or product.item_type != ItemType.FINISHED_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ko'rsatilgan ID tayyor mahsulot (FINISHED_PRODUCT) emas.",
            )

        for recipe in recipes:
            material = inventory_map.get(recipe.material_id)
            if not material:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Xom ashyo (ID={recipe.material_id}) omborda topilmadi.",
                )

            total_required = recipe.required_quantity * request.quantity

            if material.stock < total_required:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Omborda '{material.name}' yetarli emas! "
                        f"Kerak: {total_required} {material.unit}, "
                        f"Mavjud: {material.stock} {material.unit}."
                    ),
                )

            material.stock -= total_required

        product.stock += request.quantity

        prod_log = ProductionLog(
            product_id=product.id,
            quantity_produced=request.quantity,
        )
        session.add(prod_log)
        await session.flush()

    return ProduceResponse(
        message=f"{request.quantity} dona '{product.name}' muvaffaqiyatli ishlab chiqarildi.",
        production_log=ProductionLogResponse.model_validate(prod_log),
        updated_inventory=[
            InventoryResponse.model_validate(item) for item in inventory_map.values()
        ],
    )