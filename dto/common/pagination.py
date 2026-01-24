from pydantic import BaseModel, Field

class PaginationDTO(BaseModel):
    """
    Standard pagination metadata
    """
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    total: int = Field(0, ge=0)
    total_pages: int = Field(0, ge=0)
    has_next: bool = False
    has_prev: bool = False
