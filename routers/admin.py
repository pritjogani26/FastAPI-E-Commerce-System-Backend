#routers/user.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import models, schemas_users, schemas_products
from authentication_file import oauth2
from database_file.database import get_db
from repository import adminrepo

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)

role1 = models.UserRoleEnum.admin
role2 = models.UserRoleEnum.employee
role3 = models.UserRoleEnum.customer

@router.get('/list_all_user')
def admin_view(db : Session = Depends(get_db), current_user: models.Users = Depends(oauth2.require_roles(role1))):
    return adminrepo.list_all_user(db)

    
@router.get('/get_user/{id}', response_model=schemas_users.DisplayUser)
def get_user(id : str, db : Session = Depends(get_db), current_user: models.Users = Depends(oauth2.require_roles(role1))):
    return adminrepo.get_user(id, db)

@router.get('/get_past_week_order', response_model=List[schemas_products.OrderDisplayForAdmin])
def get_past_week_order(db : Session = Depends(get_db), current_user: models.Users = Depends(oauth2.require_roles(role1))):
    return adminrepo.get_past_week_order(db)