# repository/userrepo.py
from fastapi import status, HTTPException
from sqlalchemy.orm import Session, joinedload

from email_file import email_with_html
from database_file import models, schemas_users
from authentication_file.hashing import Hash
from repository import generator
from database_file.models import UserRoleEnum

def create_user(request: schemas_users.RegisterUser, db : Session):
    try :
        user = db.query(models.Users).filter(models.Users.email == request.email).first()
        if user:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email is already Register.")
        
        new_user_id = generator.generate_new_user_id(db)
        
        
        u_role = UserRoleEnum.customer
        if request.role.lower() == "admin":
            u_role = UserRoleEnum.admin
        elif request.role.lower() == "employee":
            u_role = UserRoleEnum.employee
        hashedPassword = Hash.bcrypt(request.password)
        new_user = models.Users(
                            user_id = new_user_id,
                            name = request.name, 
                            email = request.email,
                            role = u_role,
                            password = hashedPassword,
                            active_status = False
        )
        address = request.address
        new_address = models.Address(
                                customer_id = new_user_id,
                                address_type = address.address_type,
                                address_line_1 = address.address_line_1,
                                address_line_2 = address.address_line_2,
                                area = address.area,
                                city = address.city,
                                state = address.state,
                                pincode = address.pincode
        )
        
        email_with_html.send_otp.delay(request.email, request.name, 1)

        db.add(new_user)
        db.add(new_address)
        db.commit()
        db.refresh(new_user)
        db.refresh(new_address)

        user_with_address = db.query(models.Users).options(joinedload(models.Users.addresses)).filter(models.Users.user_id == new_user.user_id).first()
        return user_with_address
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
    

def verify_email(email:str,otp:int, db : Session):
    return email_with_html.otp_verification(email, otp, db)

def update_user(id: int, request: schemas_users.UpdateUser, db: Session):
    user = db.query(models.Users).filter(models.Users.user_id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if request.name:
        user.name = request.name
    if request.role:
        user.role = UserRoleEnum.customer
        if request.role.lower() == "admin":
            user.role = UserRoleEnum.admin
        elif request.role.lower() == "employee":
            user.role = UserRoleEnum.employee
    

    db.commit()
    db.refresh(user)
    return user