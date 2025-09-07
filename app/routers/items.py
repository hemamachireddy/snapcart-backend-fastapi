from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models import Item
from ..schemas import ItemIn, ItemOut

router = APIRouter(prefix="/api/items", tags=["items"])

@router.get("", response_model=List[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    category: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    sort: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    query = db.query(Item)
    if q:
        query = query.filter(Item.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Item.category == category)
    if minPrice is not None:
        query = query.filter(Item.price >= minPrice)
    if maxPrice is not None:
        query = query.filter(Item.price <= maxPrice)
    if sort == "price_asc":
        query = query.order_by(Item.price.asc())
    if sort == "price_desc":
        query = query.order_by(Item.price.desc())
    return query.limit(limit).offset(offset).all()

@router.post("", response_model=ItemOut)
def create_item(body: ItemIn, db: Session = Depends(get_db)):
    it = Item(**body.model_dump()); db.add(it); db.commit(); db.refresh(it)
    return it

@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, body: ItemIn, db: Session = Depends(get_db)):
    it = db.get(Item, item_id)
    if not it:
        raise HTTPException(404, "Item not found")
    for k, v in body.model_dump().items():
        setattr(it, k, v)
    db.commit(); db.refresh(it)
    return it

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    it = db.get(Item, item_id)
    if not it:
        raise HTTPException(404, "Item not found")
    db.delete(it); db.commit()
    return {"ok": True}
