# email_file/email_for_order.py
from celery import Celery
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()

celery_app = Celery(
    'worker',
    broker="redis://localhost:6379/0",
    backend='redis://localhost:6379/0'
)
# celery_app.autodiscover_tasks(['email_file'])

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'email_file'))

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(context)

def send_html_email(to_email: str, subject: str, html_content=""):
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
        html = render_template("order_conformation.html", {
            "name": user_name,
            "details": details
        })
        send_html_email(to_email=to_email, subject=f"Order Confirmation", html_content=html)
        # return True
    except Exception as e:
        print(f"Error sending order email: {e}")
        # return False
