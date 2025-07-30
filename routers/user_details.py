# routers/user_details.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session


from authentication_file.hashing import Hash
from database_file import models, schemas_users
from authentication_file import oauth2
from database_file.database import get_db
from email_file import email_with_html
from repository import userrepo

router = APIRouter(
    prefix="/user",
    # tags=['Users']
)

@router.get('/me', response_model=schemas_users.DisplayUser, tags=['Show'])
def get_current_user_details(current_user: models.Users = Depends(oauth2.get_current_active_user)):
    return current_user

@router.put('/update', response_model=schemas_users.DisplayUser, tags=['Update'])
def update_current_user(
    request: schemas_users.UpdateUser,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(oauth2.get_current_active_user)
    ):
    return userrepo.update_user(current_user.id, request, db)

@router.post('/reset-password-request', tags=['Update'])
def reset_password_request(email: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if email_with_html.send_reset_otp(email, user.name):
        return {"msg": "OTP sent to your email for password reset."}
    
@router.post('/reset-password', tags=['Update'])
def reset_password(email: str, otp: int, new_password: str, db: Session = Depends(get_db)):
    if not email_with_html.otp_verification(email, otp, db):
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.password = Hash.bcrypt(new_password)
    db.commit()
    return {"msg": "Password reset successful."}