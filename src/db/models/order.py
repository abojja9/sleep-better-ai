from pydantic import BaseModel, Field

class OrderRequest(BaseModel):
    answer: str = Field(..., description="Human-friendly text to show to the user")
    command: str = Field(..., description="Command for the Orders Tool")
    arguments: dict = Field(
        default_factory=dict,
        description="Command arguments including customer_id, product_name, size, and price"
    )

    class Config:
        json_schema_extra = {
            "required": ["answer", "command", "arguments"]
        }