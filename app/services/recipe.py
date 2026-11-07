from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory, ItemType, Recipe
from app.schemas.inventory import RecipeCreate


async def create_recipe(session: AsyncSession, request: RecipeCreate) -> Recipe:
    if request.product_id == request.material_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mahsulot o'zi uchun xom ashyo bo'la olmaydi.",
        )

    try:
        async with session.begin():
            items_stmt = select(Inventory).where(
                Inventory.id.in_({request.product_id, request.material_id})
            )
            items_result = await session.execute(items_stmt)
            items_map: dict[int, Inventory] = {
                item.id: item for item in items_result.scalars().all()
            }

            product = items_map.get(request.product_id)
            if not product or product.item_type != ItemType.FINISHED_PRODUCT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Mahsulot (ID={request.product_id}) topilmadi "
                        "yoki u tayyor mahsulot (FINISHED_PRODUCT) emas."
                    ),
                )

            material = items_map.get(request.material_id)
            if not material or material.item_type != ItemType.RAW_MATERIAL:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Xom ashyo (ID={request.material_id}) topilmadi "
                        "yoki u xom ashyo (RAW_MATERIAL) emas."
                    ),
                )

            exists_stmt = select(Recipe.id).where(
                Recipe.product_id == request.product_id,
                Recipe.material_id == request.material_id,
            )
            exists_result = await session.execute(exists_stmt)

            if exists_result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"'{product.name}' retseptida '{material.name}' allaqachon bor."
                    ),
                )

            recipe = Recipe(**request.model_dump())
            session.add(recipe)
            await session.flush()
    except IntegrityError:
        # Parallel so'rov xuddi shu juftlikni bizdan oldin yozib ulgurgan holat
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu xom ashyo mahsulot retseptida allaqachon bor.",
        )

    return recipe
