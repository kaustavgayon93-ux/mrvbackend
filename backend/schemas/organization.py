from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr

class OrganizationCreate(BaseModel):
    name: str
    country_code: str = "IN"
    contact_email: Optional[EmailStr] = None

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    country_code: str
    contact_email: Optional[EmailStr] = None
    created_at: datetime

    model_config = {"from_attributes": True}
