from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class BlockType(str, Enum):
    HEADER = "header"
    PARAGRAPH = "paragraph"
    KEY_VALUE = "key_value"
    TABLE_REGION = "table_region"
    FOOTER = "footer"
    FIGURE = "figure"

class BoundingBox(BaseModel):
    x0: float = Field(..., ge=0.0, le=1.0, description="Normalized top-left X (0.0 - 1.0)")
    y0: float = Field(..., ge=0.0, le=1.0, description="Normalized top-left Y (0.0 - 1.0)")
    x1: float = Field(..., ge=0.0, le=1.0, description="Normalized bottom-right X (0.0 - 1.0)")
    y1: float = Field(..., ge=0.0, le=1.0, description="Normalized bottom-right Y (0.0 - 1.0)")

    @property
    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    @property
    def height(self) -> float:
        return max(0.0, self.y1 - self.y0)

    @property
    def area(self) -> float:
        return self.width * self.height

    def overlaps(self, other: "BoundingBox") -> bool:
        """Returns True if this bounding box intersects with another."""
        return not (
            self.x1 < other.x0 or self.x0 > other.x1 or
            self.y1 < other.y0 or self.y0 > other.y1
        )

class DocumentBlock(BaseModel):
    block_id: str
    page_index: int
    block_type: BlockType
    text: str
    bbox: BoundingBox
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParsedPage(BaseModel):
    page_index: int
    width_px: int
    height_px: int
    dpi: int = 300
    blocks: List[DocumentBlock] = Field(default_factory=list)
    raw_text: str = ""

class ParsedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_pages: int
    pages: List[ParsedPage] = Field(default_factory=list)
    created_at: float
