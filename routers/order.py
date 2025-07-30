# routers/order.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import models, schemas_products
from authentication_file import oauth2
from database_file.database import get_db
from repository import orderhistoryrepo, orderrepo

router = APIRouter(
    prefix="/order",
    tags=['Order']
)

role1 = models.UserRoleEnum.admin
role2 = models.UserRoleEnum.employee
role3 = models.UserRoleEnum.customer

@router.post("/place", status_code=status.HTTP_201_CREATED, response_model=schemas_products.OrderDisplay)
def place_order(
    request: schemas_products.OrderCreateSingle,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.get_current_active_user)
):
    return orderrepo.create_order(request, db, current_user)


@router.get("/my-orders", response_model=schemas_products.PastOrdersDisplay)
def get_user_orders(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.get_current_active_user)
):
    return orderhistoryrepo.past_orders(db=db, user=current_user)

@router.get("/order_search/{order_id}", response_model=schemas_products.OrderDisplay)
def get_order_by_id(
    order_id: str, 
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.get_current_active_user)
    ):
    return orderhistoryrepo.past_orders_by_id(order_id, db)


@router.put("/cancel/{order_id}")
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user : models.Users=Depends(oauth2.get_current_active_user)
):
    return orderrepo.cancel_order(order_id, db, current_user.user_id)

