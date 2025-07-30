# repository/adminrepo.py
from datetime import datetime, timedelta
from fastapi import status, HTTPException
from sqlalchemy.orm import Session, joinedload

from database_file import models


def list_all_user(db : Session):
    users = db.query(models.Users).all()
    return users

def get_user(id : str, db: Session):
    user = db.query(models.Users).filter(models.Users.user_id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User is not found with this ID : {id}")
    return user


def get_past_week_order(db: Session):
    last_week = datetime.now() - timedelta(days=7)

    orders = (
        db.query(models.Orders)
        .options(joinedload(models.Orders.order_details).joinedload(models.OrderDetails.product))
        .filter(models.Orders.order_date >= last_week)
        .all()
    )

    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found in the past week.")

    order_list = []
    for order in orders:
        customer = db.query(models.Users).filter(models.Users.user_id == order.customer_id).first()
        if not customer:
            continue

        product_list = []
        total = 0.0

        for detail in order.order_details:
            product = detail.product
            product_data = {
                "quantity": detail.quantity,
                "product_name": product.product_name,
                "price": product.price,
                "quantity" : detail.quantity,
                "subtotal" : product.price * detail.quantity
            }
            total += product.price * detail.quantity
            product_list.append(product_data)

        order_data = {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "customer_id": customer.user_id,
            "address": order.address,
            "status" : order.status,
            "products": product_list,
            "total_amount": total,
        }
        order_list.append(order_data)

    return order_list