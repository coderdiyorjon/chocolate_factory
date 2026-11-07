import enum
from datetime import datetime

from sqlalchemy import (CheckConstraint, DateTime, Enum, ForeignKey, Integer,
                        String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ItemType(str, enum.Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    FINISHED_PRODUCT = "FINISHED_PRODUCT"


class Inventory(Base):
    __tablename__ = "inventory"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType, name="item_type"), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_is_positive"),
    )
    # Fetch server-generated updated_at via RETURNING so it is never lazy-loaded in async code.
    __mapper_args__ = {"eager_defaults": True}


class Recipe(Base):
    __tablename__ = "recipes"
    
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.id", ondelete="RESTRICT"), nullable=False
    )
    required_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("product_id", "material_id", name="unique_product_material_idx"),
        CheckConstraint("required_quantity > 0", name="check_required_Quantity_is_positive"),
    )


class ProductionLog(Base):
    __tablename__ = "production_logs"
    
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    quantity_produced: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
