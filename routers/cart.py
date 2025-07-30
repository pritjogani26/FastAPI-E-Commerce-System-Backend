# routers/cart.py
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import models, schemas_products
from authentication_file import oauth2
from database_file.database import get_db
from repository import cartrepo
from repository.generator import get_session_id

router = APIRouter(
    prefix="/cart",
    tags=['Cart']
)

role1 = models.UserRoleEnum.admin
role2 = models.UserRoleEnum.employee
role3 = models.UserRoleEnum.customer

@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=List[schemas_products.CartProductOut])
def add_to_cart(
    request: schemas_products.OrderProductInput,
    req: Request,
    db: Session = Depends(get_db),
    current_user: Optional[models.Users] = Depends(oauth2.get_current_active_user_optional)
):
    if current_user:
        return cartrepo.add_to_cart(request, db, user_id = current_user.user_id)
    else:
        session_id = get_session_id(req)
        print(session_id)
        return cartrepo.add_to_cart(request, db, session_id = session_id)

@router.get("/display", status_code=status.HTTP_302_FOUND, response_model=List[schemas_products.CartProductOut])
def show_your_cart(
    req : Request,
    db: Session = Depends(get_db),
    current_user: Optional[models.Users] = Depends(oauth2.get_current_active_user_optional)
):
    if current_user:
        return cartrepo.display_cart(db, user_id=current_user.user_id)
    else:
        session_id = get_session_id(req)
        print(session_id)
        return cartrepo.display_cart(db, session_id=session_id)

@router.post("/checkout", status_code=status.HTTP_201_CREATED, response_model=schemas_products.OrderDisplay)
def check_out(
    address_id :int = None,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.get_current_active_user)
):
    return cartrepo.check_out(address_id, db, current_user)

@router.put("/edit")
def update_cart_item(
    req : Request,
    request: schemas_products.EditCartItem, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.Users] = Depends(oauth2.get_current_active_user_optional)
    ):
    
    if current_user:
        return cartrepo.edit_cart_item(request, db, user_id=current_user.user_id)
    else:
        session_id = get_session_id(req)
        print(session_id)
        return cartrepo.edit_cart_item(request, db, session_id = session_id)
