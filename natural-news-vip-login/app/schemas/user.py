from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional


# Define Enum Types
class PlatformEnum(str, Enum):
    SHOPIFY = "Shopify"
    HRS = "HRS"

class TierEnum(str, Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

# User Schema for Request
class UserCreate(BaseModel):
    email: EmailStr
    type_platform: PlatformEnum
    tier: Optional[TierEnum] = TierEnum.BRONZE  # ✅ Default value

# User Schema for Response
class UserResponse(BaseModel):
    id: int
    email: str
    type_platform: PlatformEnum
    tier: TierEnum
    reward: int

    class Config:
        from_attributes = True  # Allows ORM mode

class LoginResponse(BaseModel):
    access_token: str
    token_type: str