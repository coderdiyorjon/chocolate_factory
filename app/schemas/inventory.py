from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory import ItemType


class InventoryResponse(BaseModel):
    id: int
    name: str
    item_type: ItemType
    stock: int
    unit: str
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProduceRequest(BaseModel):
    product_id: int = Field(
        default=3,
        gt=0,
        description="Dark Chocolate",
    )
    quantity: int = Field(
        default=1,
        gt=0,
        description="Quantity of the product to produce",
    )


class ProductionLogResponse(BaseModel):
    id: int
    product_id: int
    quantity_produced: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProduceResponse(BaseModel):
    message: str
    production_log: ProductionLogResponse
    updated_inventory: list[InventoryResponse]
