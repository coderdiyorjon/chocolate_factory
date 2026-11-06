import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models
from app.db.session import AsyncSessionLocal, Base, engine
from app.models.inventory import Inventory, ItemType, Recipe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables() -> None:
    async with engine.begin() as conn:
        logger.info("Creating Tabls...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully.")


async def seed_data(session: AsyncSession) -> None:
    stmt = select(Inventory).limit(1)
    result = await session.execute(stmt)
    if result.scalars().first() is not None:
        logger.info("Data already exists. Skipping seeding")
        return
    logger.info("Seeding initial data")
    
    cocoa = Inventory(
        name = "Cocoa",
        item_type=ItemType.RAW_MATERIAL,
        stock=500,
        unit="g",
    )    
    sugar = Inventory(
        name="Sugar",
        item_type=ItemType.RAW_MATERIAL,
        stock=500,
        unit='g',
    )
    dark_chocolate = Inventory(
        name="Dark chocolate",
        item_type=ItemType.FINISHED_PRODUCT,
        stock=0,
        unit='pcs',
    )
    session.add(cocoa)
    session.add(sugar)
    session.add(dark_chocolate)
    await session.flush()

    recipe_cocoa = Recipe(
        product_id=dark_chocolate.id,
        material_id=cocoa.id,
        required_quantity=50,
    )
    recipe_sugar = Recipe(
        product_id=dark_chocolate.id,
        material_id=sugar.id,
        required_quantity=50,
    )
    session.add_all([recipe_cocoa, recipe_sugar])
    await session.commit()
    
    logger.info("Initial data successfully added.")


async def main() -> None:
    await create_tables()
    async with AsyncSessionLocal() as session:
        await seed_data(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
