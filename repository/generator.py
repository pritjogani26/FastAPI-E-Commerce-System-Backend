# repository/generator.py
from typing import Optional
import uuid
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from database_file import models

from database_file import models


def generate_new_user_id(db: Session):
    latest_user = db.query(models.Users).order_by(models.Users.user_id.desc()).first()
    if latest_user:
        last_id = int(latest_user.user_id.replace("User", ""))
        new_id = f"User{last_id + 1:05d}"
    else:
        new_id = "User00001"
    return new_id

def generate_new_Order_id(db: Session):
    latest_order = db.query(models.Orders).order_by(models.Orders.order_id.desc()).first()
    if latest_order:
        last_id = int(latest_order.order_id.replace("Order", ""))
        new_id = f"Order{last_id + 1:05d}"
    else:
        new_id = "Order00001"
    return new_id

def get_user_address(db: Session, user_id: str, address_id: Optional[int] = None):
    if address_id:
        address = db.query(models.Address).filter(
            models.Address.address_id == address_id,
            models.Address.customer_id == user_id
        ).first()

        if not address:
            raise HTTPException(
                status_code=404,
                detail="Provided address not found or does not belong to the user."
            )
    else:
        address = db.query(models.Address).filter(
            models.Address.customer_id == user_id
        ).first()

        if not address:
            raise HTTPException(
                status_code=400,
                detail="No address found for user. Please add one before placing an order."
            )
    address_str = f"{address.address_line_1}, {address.address_line_2}, {address.area}, {address.city}, {address.state}, {address.pincode}"
    return address_str


def get_session_id(request: Request) -> str:
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
    return session_id