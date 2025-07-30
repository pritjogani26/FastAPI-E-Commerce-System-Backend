# routers/product.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import models, schemas_products
from authentication_file import oauth2
from database_file.database import get_db
from repository import productrepo

router = APIRouter(
    prefix="/product",
    tags=['Product']
)

role1 = models.UserRoleEnum.admin
role2 = models.UserRoleEnum.employee
role3 = models.UserRoleEnum.customer

@router.post('/Add', response_model=schemas_products.DisplayProduct) # , tags=['Add Product']
def add(
    request: schemas_products.AddProduct,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.require_roles(role1, role2))
    ):
    
    return productrepo.add_product(request, db)


@router.get("/Display_All", response_model=List[schemas_products.DisplayProduct])
def Display_All(
    db: Session = Depends(get_db)
):
    return productrepo.list_products(db)

@router.get("/Search_by_id_or_name", response_model=schemas_products.DisplayProduct)
def search_by_id_or_name(
    product_name: str = "",
    id: int = 0,
    db: Session = Depends(get_db)
):
    return productrepo.list_product(db, id=id, name=product_name)

@router.put("/Update_Stock", response_model=schemas_products.DisplayProduct)
def Update_Stock(
    id : int = 0,
    Stock_Increase_By: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.require_roles(role1, role2))
):
    return productrepo.update_product_stock(db, id, Stock_Increase_By)

