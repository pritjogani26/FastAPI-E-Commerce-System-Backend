# repository/cartrepo.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database_file import models, schemas_products
from repository import generator
from database_file.models import CartStatusEnum
from repository import cart_helpers

def add_to_cart(request: schemas_products.OrderProductInput, db: Session, user_id: str = None, session_id: str = None):
    product = cart_helpers.get_product(db, request.product_id)
    cart_helpers.validate_quantity(product, request.quantity)

    get_cart = cart_helpers.get_or_create_cart(db, user_id, session_id)

    existing_item = cart_helpers.get_cart_item(db, get_cart.cart_id, product.product_id)

    if existing_item:
        existing_item.quantity += request.quantity
    else:
        cart_detail = models.CartDetails(
            cart_id=get_cart.cart_id,
            product_id=product.product_id,
            quantity=request.quantity
        )
        db.add(cart_detail)

    db.commit()

    result = cart_helpers.get_cart_items_with_products(db, get_cart.cart_id)

    return [
        schemas_products.CartProductOut(
            cart_detail_id=cart_detail.cart_detail_id,
            product_id=product.product_id,
            product_name=product.product_name,
            price=product.price,
            quantity=cart_detail.quantity
        )
        for cart_detail, product in result
    ]

def display_cart(db: Session, user_id: str = None, session_id: str = None):
    existing_cart = cart_helpers.get_active_cart(db, user_id, session_id)

    result = cart_helpers.get_cart_items_with_products(db, existing_cart.cart_id)

    return [
        schemas_products.CartProductOut(
            cart_detail_id=cart_detail.cart_detail_id,
            product_id=product.product_id,
            product_name=product.product_name,
            price=product.price,
            quantity=cart_detail.quantity
        )
        for cart_detail, product in result
    ]

def check_out(address_id, db: Session, user: models.Users):
    try:
        existing_cart = cart_helpers.get_active_cart(db, user.user_id)

        cart_items = db.query(models.CartDetails).filter(
            models.CartDetails.cart_id == existing_cart.cart_id
        ).all()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty.")

        order_items = []
        for item in cart_items:
            product = cart_helpers.get_product(db, item.product_id)
            cart_helpers.validate_quantity(product, item.quantity)
            order_items.append((product, item.quantity))

        address_str = generator.get_user_address(db, user.user_id, address_id)
        new_order_id = generator.generate_new_Order_id(db)
        # new_order = models.Orders(
        #     order_id=new_order_id,
        #     customer_id=user.user_id,
        #     address=address_str
        # )
        # db.add(new_order)
        # db.commit()
        # db.refresh(new_order)

        t_amount = 0
        ordered_products_response = []
        for product, qty in order_items:
            order_detail = models.OrderDetails(
                order_id=new_order_id,
                product_id=product.product_id,
                quantity=qty,
                price=product.price
            )
            db.add(order_detail)
            t_amount += qty * product.price
            product.unit -= qty
            db.add(product)

            ordered_products_response.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "quantity": qty,
                "price": product.price,
                "subtotal": qty * product.price
            })
            
            
        new_order = models.Orders(
            order_id=new_order_id,
            customer_id=user.user_id,
            address=address_str,
            total_amount = t_amount
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        existing_cart.status = CartStatusEnum.checked_out
        db.add(existing_cart)

        db.query(models.CartDetails).filter(
            models.CartDetails.cart_id == existing_cart.cart_id
        ).delete()

        db.commit()

        from email_file import email_for_order
        email_for_order.send_order_details_email.delay(user.email, user.name, {
            "order_id": new_order.order_id,
            "address": address_str,
            "order_date": new_order.order_date.strftime("%Y-%m-%d %H:%M"),
            "products": ordered_products_response,
            "total_amount": t_amount
        })

        return {
            "message": "Order placed successfully.",
            "order_id": new_order.order_id,
            "customer_name": user.name,
            "status": new_order.status,
            "customer_id": new_order.customer_id,
            "address": address_str,
            "order_date": new_order.order_date,
            "products": ordered_products_response,
            "total_amount": t_amount
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def edit_cart_item(request: schemas_products.EditCartItem, db: Session, user_id: str = None, session_id: str = None):
    existing_cart = cart_helpers.get_active_cart(db, user_id, session_id)

    cart_item = cart_helpers.get_cart_item(db, existing_cart.cart_id, request.product_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart.")

    product = cart_helpers.get_product(db, request.product_id)

    if request.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return {"message": f"Product '{product.product_name}' removed from cart."}

    cart_helpers.validate_quantity(product, request.quantity)
    cart_item.quantity = request.quantity
    db.commit()

    return {
        "message": f"Cart updated: '{product.product_name}' quantity set to {request.quantity}."
    }