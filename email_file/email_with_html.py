# email_file/email_with_html.py

from celery import Celery
import secrets
import smtplib
from email.message import EmailMessage
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from redis_file import email_store_with_redis
from database_file import models
from jinja2 import Environment, FileSystemLoader

load_dotenv()

celery_app = Celery(
    'worker',
    broker="redis://localhost:6379/0",
    backend='redis://localhost:6379/0'
)
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'email_file'))

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(context)

def send_html_email(to_email: str, subject: str, html_content = ""):
    if not html_content:
        raise ValueError("Missing HTML content for email.")
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg.set_content("This is an HTML email. Please view it in an HTML-compatible client.")
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP(os.getenv("EMAIL_SERVER"), int(os.getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)

@celery_app.task(name="send_otp")
def send_otp(to_u_email: str, user_name:str = "User", code:int =  1):
    try:
        otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        print(otp)

        if code == 1:
            html = render_template("verification_email.html", {"name": user_name, "otp": otp})
            send_html_email(to_email=to_u_email, subject=f"Varify Email Here {user_name}", html_content=html)
        else:
            html = render_template("reset_password.html", {"name": user_name, "otp": otp})
            send_html_email(to_email=to_u_email, subject=f"Confirm your Email Here {user_name}", html_content=html)
        
        email_store_with_redis.store_email_verification(to_u_email, otp)
        print("Success")
        return True
    

    except Exception as e:
        print(f"Error while sending OTP: {e}")
        raise HTTPException(status_code=409, detail="Email OTP sending failed. Try Again...")

# OTP verification logic
def otp_verification(email: str, otp: int, db: Session):
    email_user = db.query(models.Users).filter(models.Users.email == email).first()

    if not email_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Wrong Email.")

    record = email_store_with_redis.get_email_verification(email)
    if not record:
        send_otp.delay(email, email_user.name)
        raise HTTPException(status_code=404, detail="OTP expired or not found")
    if int(record["otp"]) != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")


    email_user.active_status = True
    db.commit()
    db.refresh(email_user)
    email_store_with_redis.delete_email_verification(email)
    return email_user

# Reuse send_otp for password reset
def send_reset_otp(to_email: str, user_name):
    return send_otp.delay(to_email, user_name, 0)


# Order Details E-Mail
def render_template1(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(context)

def send_html_email1(to_email: str, subject: str, html_content=""):
    if not html_content:
        raise ValueError("Missing HTML content for email.")
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg.set_content("This is an HTML email. Please view it in an HTML-compatible client.")
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP(os.getenv("EMAIL_SERVER"), int(os.getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)

@celery_app.task(name="email_file.send_order_details_email")
def send_order_details_email(to_email: str, user_name: str, details: dict):
    try:
        html = render_template1("order_conformation.html", {
            "name": user_name,
            "details": details
        })
        send_html_email1(to_email=to_email, subject=f"Order Confirmation Email", html_content=html)
        print("Success")
    except Exception as e:
        print(f"Error sending order email: {e}")