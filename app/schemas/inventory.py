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


class InventoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Milk"],
        description="Unique name of the item",
    )
    item_type: ItemType = Field(
        examples=[ItemType.RAW_MATERIAL],
        description="RAW_MATERIAL or FINISHED_PRODUCT",
    )
    stock: int = Field(
        default=0,
        ge=0,
        le=1_000_000,
        description="Initial stock",
    )
    unit: str = Field(
        min_length=1,
        max_length=20,
        examples=["g"],
        description="Unit of measure: g, pcs",
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class RestockRequest(BaseModel):
    quantity: int = Field(
        gt=0,
        le=1_000_000,
        examples=[500],
        description="Quantity to add to the stock",
    )


class RecipeCreate(BaseModel):
    product_id: int = Field(
        gt=0,
        examples=[3],
        description="ID of the FINISHED_PRODUCT",
    )
    material_id: int = Field(
        gt=0,
        examples=[1],
        description="ID of the RAW_MATERIAL",
    )
    required_quantity: int = Field(
        gt=0,
        le=1_000_000,
        examples=[50],
        description="Quantity of the material for 1 unit of the product",
    )


class RecipeResponse(BaseModel):
    id: int
    product_id: int
    material_id: int
    required_quantity: int

    model_config = ConfigDict(from_attributes=True)
