# repository/orderrepo.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database_file import models, schemas_products

from email_file import email_with_html
from repository import generator
from database_file import models

def create_order(request: schemas_products.OrderCreateSingle, db: Session, user: models.Users):
    try:
        if not request.product_id:
            raise HTTPException(status_code=400, detail="Product ID is required.")
        if request.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1.")

        # Fetch product
        product = db.query(models.Products).filter(models.Products.product_id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {request.product_id} not found.")
        
        if product.unit < request.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{product.product_name}'. Available: {product.unit}, Requested: {request.quantity}"
            )

        address_str = generator.get_user_address(db, user.user_id, request.address_id)
        new_order_id = generator.generate_new_Order_id(db)
        total_amount = request.quantity * product.price
        # Create new order
        new_order = models.Orders(
            order_id = new_order_id,
            customer_id=user.user_id,
            address=address_str,
            total_amount = total_amount
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # Create order detail
        order_detail = models.OrderDetails(
            order_id=new_order.order_id,
            product_id=product.product_id,
            quantity=request.quantity,
            price=product.price
        )
        db.add(order_detail)

        # Update stock
        product.unit -= request.quantity
        db.add(product)

        total_amount = request.quantity * product.price

        db.commit()

        # Send email
        email_with_html.send_order_details_email.delay(
            user.email,
            user.name,
            {
                "order_id": new_order.order_id,
                
                "order_date": new_order.order_date.strftime("%Y-%m-%d %H:%M"),
                "address": address_str,
                "products": [{
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "quantity": request.quantity,
                    "price": product.price,
                    "subtotal" : product.price * request.quantity
                }],
                "total_amount": total_amount
            }
        )

        return {
            "status": "Order placed successfully.",
            "order_id": new_order.order_id,
            "customer_id" : new_order.customer_id,
            "customer_name": user.name,
            "status": new_order.status,  
            "customer_name" : user.name,
            "order_date": new_order.order_date,
            "address": address_str,
            "products": [{
                "product_name": product.product_name,
                "quantity": request.quantity,
                "price": product.price,
                "subtotal" : product.price * request.quantity
            }],
            "total_amount": total_amount
        }
        
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




def cancel_order(order_id: str, db: Session, user_id: str):

    order = db.query(models.Orders).filter(
        models.Orders.order_id == order_id,
        models.Orders.customer_id == user_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found or does not belong to user.")

    if order.status == models.OrderStatusEnum.cancelled:
        raise HTTPException(status_code=400, detail="Order is already cancelled.")

    order_details = db.query(models.OrderDetails).filter(models.OrderDetails.order_id == order_id).all()

    for item in order_details:
        product = db.query(models.Products).filter(models.Products.product_id == item.product_id).first()
        if product:
            product.unit += item.quantity

    order.status = models.OrderStatusEnum.cancelled

    db.commit()

    return {
        "message": f"Order {order_id} has been cancelled.",
        "status": order.status
    }


