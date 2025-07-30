# routers/category.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import models, schemas_products
from authentication_file import oauth2
from database_file.database import get_db
from repository import productrepo
from database_file.models import UserRoleEnum

router = APIRouter(
    prefix="/category",
    tags=['Category']
)

role1 = UserRoleEnum.admin
role2 = UserRoleEnum.employee
role3 = UserRoleEnum.customer

@router.post('/create', response_model=schemas_products.DisplayCategory) 
def create_category(
    request: schemas_products.AddCategory,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.require_roles(role1, role2))
    ):
    
    return productrepo.create_category(request, db)


@router.get("/Display_All", response_model=List[schemas_products.DisplayCategory])
def Display_All(
    db: Session = Depends(get_db)
):
    return productrepo.list_categories(db)


@router.get("/Search_by_name_or_id", response_model=schemas_products.DisplayCategory)
def Search_by_name_or_id(
    category_name : str = "",
    id : int = 0,
    db: Session = Depends(get_db)
):
    return productrepo.list_category(db, id, category_name)