from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class OrganizationCreate(BaseModel):
    name: str
    country_code: str = "IN"
    contact_email: EmailStr

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    country_code: str
    contact_email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
