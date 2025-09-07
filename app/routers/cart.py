from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Cart, CartItem, Item
from ..schemas import CartOut
from ..deps import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])

def _ensure_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart); db.commit(); db.refresh(cart)
    return cart

@router.get("", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), user = Depends(get_current_user)):
    cart = _ensure_cart(db, user.id)
    lines = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    total = sum(float(li.item.price) * li.qty for li in lines)
    return {"items": lines, "total": total}

@router.post("/add")
def add(item_id: int, qty: int = 1, db: Session = Depends(get_db), user = Depends(get_current_user)):
    cart = _ensure_cart(db, user.id)
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    line = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.item_id == item_id).first()
    if line:
        line.qty += max(1, qty)
    else:
        db.add(CartItem(cart_id=cart.id, item_id=item_id, qty=max(1, qty)))
    db.commit()
    return {"ok": True}

@router.post("/remove")
def remove(item_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    cart = _ensure_cart(db, user.id)
    line = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.item_id == item_id).first()
    if not line:
        raise HTTPException(404, "Not in cart")
    db.delete(line); db.commit()
    return {"ok": True}

@router.post("/clear")
def clear(db: Session = Depends(get_db), user = Depends(get_current_user)):
    cart = _ensure_cart(db, user.id)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"ok": True}
