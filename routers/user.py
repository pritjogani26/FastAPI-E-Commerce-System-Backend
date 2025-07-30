#routers/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from database_file import schemas_users
from database_file.database import get_db
from repository import userrepo

router = APIRouter(
    prefix="/user",
)

@router.post('/', response_model=schemas_users.DisplayUser, tags=['Create'])
def create_user(request : schemas_users.RegisterUser, db: Session = Depends(get_db)) :
    return userrepo.create_user(request, db)

@router.get('/email_verify', response_model=schemas_users.DisplayUser,  tags=['Create'])
def email_verification(email : str, otp : int, db: Session = Depends(get_db)) :
    return userrepo.verify_email(email, otp, db)