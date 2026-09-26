from typing import Any, Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class GeoJSONPoint(BaseModel):
    type: str = Field("Point", pattern="^Point$")
    coordinates: List[float]

class GeoJSONPolygon(BaseModel):
    type: str = Field("Polygon", pattern="^Polygon$")
    coordinates: List[List[List[float]]]

class GeoJSONMultiPolygon(BaseModel):
    type: str = Field("MultiPolygon", pattern="^MultiPolygon$")
    coordinates: List[List[List[List[float]]]]

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    minio: str
