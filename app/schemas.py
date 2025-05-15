from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

    class Config:
        orm_mode = True
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LotBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_price: float = Field(..., gt=0)
    bid_step: float = Field(10.0, gt=0)
    end_time: datetime

class LotCreate(BaseModel):
    title: str
    description: str | None = None
    start_price: float
    bid_step: float
    end_time: datetime

class LotResponse(BaseModel):
    id: int
    title: str
    start_price: float
    current_price: float
    bid_step: float
    created_at: datetime
    end_time: datetime
    owner_id: int

    class Config:
        from_attributes = True

class BidBase(BaseModel):
    amount: float = Field(..., gt=0)
    lot_id: int

class BidCreate(BidBase):
    is_proxy: bool = False
    max_bid: Optional[float] = Field(None, gt=0)

    @validator('max_bid')
    def validate_max_bid(cls, v, values):
        if values.get('is_proxy') and v is None:
            raise ValueError("Max bid is required for proxy bids")
        if v is not None and v <= values.get('amount'):
            raise ValueError("Max bid must be greater than initial amount")
        return v

class BidResponse(BidBase):
    id: int
    user_id: int
    created_at: datetime
    is_proxy: bool
    max_bid: Optional[float]

    class Config:
        orm_mode = True

class BidListResponse(BaseModel):
    bids: list[BidResponse]
    count: int
