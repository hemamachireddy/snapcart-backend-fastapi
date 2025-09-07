from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

# ---------- User / Auth ----------
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class AuthIn(BaseModel):
    email: EmailStr
    password: str

class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ---------- Items ----------
class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    image_url: str

class ItemOut(ItemIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Cart ----------
class CartAddIn(BaseModel):
    item_id: int
    qty: int = 1

class CartLineOut(BaseModel):
    id: int                  # cart line id
    item: ItemOut
    qty: int
    model_config = ConfigDict(from_attributes=True)

class CartOut(BaseModel):
    items: List[CartLineOut]
    total: Decimal
