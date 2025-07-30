# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database_file.database import get_db
from database_file.models import Orders, Payment, Base, Payments
from database_file.models import OrderStatusEnum  # your enum file
import razorpay
import os

from database_file.database import engine
from database_file import models

models.Base.metadata.create_all(bind=engine)

import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/pay", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("pay.html", {"request": request})

@app.post("/pay", response_class=HTMLResponse)
async def post_order_id(request: Request, order_id: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatusEnum.pending:
        raise HTTPException(status_code=400, detail="Order is not in pending state")

    rzp_order = client.order.create({
        "amount": int(order.total_amount * 100),
        "currency": "INR",
        "receipt": f"receipt_{order_id}",
        "payment_capture": 1
    })

    return templates.TemplateResponse("pay.html", {
        "request": request,
        "order": order,
        "rzp_order": rzp_order,
        "key": os.getenv("RAZORPAY_KEY_ID")
    })


@app.post("/verify")
async def verify_payment(
    order_id: str = Form(...),
    razorpay_order_id: str = Form(...),
    razorpay_payment_id: str = Form(...),
    razorpay_signature: str = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_db)
):
    try:
        order = db.query(Orders).filter(Orders.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=400, detail="Order not found")
        
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Save payment
    payment = Payments(
        payment_id=razorpay_payment_id,
        order_id=order_id,
        amount=amount,
        currency="INR"
    )
    db.add(payment)

    # Update order status and link payment_id
    order = db.query(Orders).filter(Orders.order_id == order_id).first()
    if order:
        order.status = OrderStatusEnum.placed
        order.payment_id = razorpay_payment_id

    db.commit()

    return JSONResponse({"success": True, "payment_id": razorpay_payment_id})
