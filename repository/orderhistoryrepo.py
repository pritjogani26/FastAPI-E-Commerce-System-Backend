# repository/orderhistoryrepo.py
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from database_file import models

def past_orders(db: Session, user: models.Users):
    try:
        orders = (
            db.query(models.Orders)
            .filter(models.Orders.customer_id == user.user_id)
            .options(joinedload(models.Orders.order_details).joinedload(models.OrderDetails.product))
            .all()
        )

        if not orders:
            raise HTTPException(status_code=404, detail="No past orders found.")

        result = []

        for order in orders:
            product_list = []
            total_amount = 0.0

            for detail in order.order_details:
                product = detail.product
                if not product:
                    continue

                subtotal = detail.quantity * detail.price
                total_amount += subtotal

                product_list.append({
                    "product_name": product.product_name,
                    "quantity": detail.quantity,
                    "price": detail.price,
                    "subtotal": subtotal
                })

            result.append({
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "customer_name": user.name, 
                "status" : order.status,
                "order_date": order.order_date,
                "address": order.address,
                "total_amount": total_amount,
                "products": product_list
            })

        return {"past_orders": result}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def past_orders_by_id(order_id: str, db: Session):
    try:
        order = (
            db.query(models.Orders)
            .filter(models.Orders.order_id == order_id)
            .options(joinedload(models.Orders.order_details).joinedload(models.OrderDetails.product))
            .first()
        )
        customer = db.query(models.Users).filter(models.Orders.customer_id == models.Users.user_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="No order found with this ID.")

        if not order.order_details:
            raise HTTPException(status_code=404, detail="Order exists but has no products.")

        product_list = []
        total_amount = 0.0

        for item in order.order_details:
            product = item.product
            if not product:
                continue

            subtotal = item.quantity * item.price
            total_amount += subtotal

            product_list.append({
                "product_name": product.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": subtotal
            })

        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "customer_name": customer.name,
            "status": order.status,  
            "order_date": order.order_date,
            "total_amount": total_amount,
            "products": product_list,
            "customer_id": order.customer_id,
            "address": order.address
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
