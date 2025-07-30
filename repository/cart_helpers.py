# repository/cart_helpers.py
from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from database_file import models
from database_file.models import CartStatusEnum
from repository.generator import get_session_id

def get_product(db: Session, product_id: int) -> models.Products:
    product = db.query(models.Products).filter(models.Products.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID {product_id} not found."
        )
    return product

def validate_quantity(product: models.Products, quantity: int):
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zero or Negative Quantity Not allowed for Product: '{product.product_name}'."
        )
    if product.unit < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock for '{product.product_name}'. Available: {product.unit}, Requested: {quantity}"
        )

def get_or_create_cart(db: Session, user_id: str = None, session_id: str = None) -> models.Cart:
    query = db.query(models.Cart).filter(models.Cart.status == CartStatusEnum.active)
    cart = None

    if user_id:
        cart = query.filter(models.Cart.customer_id == user_id).first()
        if not cart:
            cart = models.Cart(customer_id=user_id)
    elif session_id:
        cart = query.filter(models.Cart.session_id == session_id).first()
        if not cart:
            cart = models.Cart(session_id=session_id)

    if not cart.cart_id:
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart

def get_active_cart(db: Session, user_id: str = None, session_id: str = None) -> models.Cart:
    query = db.query(models.Cart).filter(models.Cart.status == CartStatusEnum.active)

    if user_id:
        cart = query.filter(models.Cart.customer_id == user_id).first()
    elif session_id:
        cart = query.filter(models.Cart.session_id == session_id).first()
    else:
        cart = None

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your Cart is Empty.")

    return cart

def get_cart_item(db: Session, cart_id: int, product_id: int) -> models.CartDetails:
    return db.query(models.CartDetails).filter_by(
        cart_id=cart_id,
        product_id=product_id
    ).first()

def get_cart_items_with_products(db: Session, cart_id: int):
    return (
        db.query(models.CartDetails, models.Products)
        .join(models.Products, models.CartDetails.product_id == models.Products.product_id)
        .filter(models.CartDetails.cart_id == cart_id)
        .all()
    )

def cart_update_while_login(db: Session, req : Request, user: models.Users):
    # Get session cart
    session_id = get_session_id(req)
    print("Session ID:", session_id)

    session_cart = db.query(models.Cart).options(joinedload(models.Cart.cart_details)).filter(
        models.Cart.session_id == session_id,
        models.Cart.status == models.CartStatusEnum.active
    ).first()

    user_cart = db.query(models.Cart).filter(
        models.Cart.customer_id == user.user_id,
        models.Cart.status == models.CartStatusEnum.active
    ).first()

    if session_cart:
        if user_cart:
            # Merge session cart items into user cart
            for item in session_cart.cart_details:
                existing_item = db.query(models.CartDetails).filter_by(
                    cart_id=user_cart.cart_id,
                    product_id=item.product_id
                ).first()

                if existing_item:
                    existing_item.quantity += item.quantity
                else:
                    new_item = models.CartDetails(
                        cart_id=user_cart.cart_id,
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    db.add(new_item)

            # Delete the session cart after merging
            db.query(models.CartDetails).filter_by(cart_id=session_cart.cart_id).delete()
            db.delete(session_cart)
        else:
            # Assign session cart to user
            session_cart.customer_id = user.user_id
            session_cart.session_id = None
            db.add(session_cart)

    db.commit()