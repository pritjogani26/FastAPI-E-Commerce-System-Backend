# email_file/email_verify.py
import secrets
import smtplib
from email.message import EmailMessage
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

from database_file import models

load_dotenv()

def send_otp(to_email : str, db: Session):
    e_message = ""
    try :
        send_otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        from_main = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        server.login(from_main, password)
        
        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_main
        msg['To'] = to_email
        msg.set_content(f"Your OTP is: {send_otp}")

        server.send_message(msg)
        email_otp = models.Email_Verify(
                        email = to_email,
                        sent_at = datetime.now(timezone.utc),
                        otp = send_otp,
                        message = "Success"
        )
        db.add(email_otp)
        db.commit()
        db.refresh(email_otp)
        return True
    
        
    # except:
    except Exception as e:
            print(f"Error while sending OTP: {e}")  # This will show the real issue in terminal
            raise HTTPException(status_code=409, detail="409: Email OTP sending failed. Try Again...")
    




def otp_verification(email: str, otp: int, db: Session):
    email_data = db.query(models.Email_Verify).filter(models.Email_Verify.email == email).first()
    if not email_data:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Wrong Email. New OTP is Sent Again.")

    # Fix here
    sent_at = email_data.sent_at
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)

    time_difference = datetime.now(timezone.utc) - sent_at

    if time_difference > timedelta(minutes=10):
        db.delete(email_data)
        db.commit()
        send_otp(email, db)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="OTP expired. New OTP is Sent")

    if int(email_data.otp) == otp:
        user = db.query(models.Users).filter(models.Users.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        user.active_status = True
        db.delete(email_data)
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP.")


def send_reset_otp(to_email: str, db: Session):
    return send_otp(to_email, db)