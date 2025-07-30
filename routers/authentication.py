#routers/authentication.py
from typing import Optional
from fastapi import APIRouter, Body, Form, Request, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from authentication_file.hashing import Hash
from database_file import models, schemas_users
from database_file.database import get_db
from authentication_file import token_op
from repository import cart_helpers

router = APIRouter(
    tags=['Login']
)

def get_login_request(
    username: Optional[EmailStr] = Form(None),  # from OAuth2PasswordRequestForm
    password: Optional[str] = Form(None),
    json_body: Optional[schemas_users.LoginRequest] = Body(None)
) -> schemas_users.LoginRequest:
    if json_body:
        return json_body
    if username and password:
        return schemas_users.LoginRequest(email=username, password=password)
    raise HTTPException(status_code=422, detail="Invalid login input format.")


# @router.post('/login')
# def login(req: Request, request: schemas_users.LoginRequest = Depends(get_login_request), db: Session = Depends(get_db)):
#     user = db.query(models.Users).filter(models.Users.email == request.email).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
#     if not Hash.verify(user.password, request.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")
    
#     if user.active_status == False:
#         raise HTTPException(
#             status_code=status.HTTP_406_NOT_ACCEPTABLE,
#             detail="Your Email is Not Verified. You are not an Active User."
#         )
        
#     user.last_login = datetime.now(timezone.utc)
#     db.commit()
    
#     cart_helpers.cart_update_while_login(db, req, user)
    

#     access_token = token_op.create_access_token(data={"sub": user.email})
#     req.session["user_id"] = user.user_id
#     req.session["token"] = access_token
#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }

# Handles Swagger's OAuth2 flow (form data)
@router.post('/login', summary="Login via form", description="Used by Swagger OAuth2 form")
def login_form(
    req: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return _perform_login(req, form_data.username, form_data.password, db)


# Handles your JSON login
@router.post('/login_json', summary="Login via JSON", description="Use JSON body for login")
def login_json(
    req: Request,
    credentials: schemas_users.LoginRequest,
    db: Session = Depends(get_db)
):
    return _perform_login(req, credentials.email, credentials.password, db)


# Shared login logic
def _perform_login(req: Request, email: str, password: str, db: Session):
    user = db.query(models.Users).filter(models.Users.email == email).first()

    if not user or not Hash.verify(user.password, password):
        raise HTTPException(status_code=404, detail="Invalid credentials")

    if not user.active_status:
        raise HTTPException(status_code=406, detail="Email not verified. Inactive user.")

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    cart_helpers.cart_update_while_login(db, req, user)

    token = token_op.create_access_token(data={"sub": user.email})
    req.session["user_id"] = user.user_id
    req.session["token"] = token

    return {
        "access_token": token,
        "token_type": "bearer"
    }
