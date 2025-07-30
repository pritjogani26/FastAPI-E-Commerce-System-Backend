from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    category_name: str
    description: str

    class Config:
        orm_mode = True

class CategoryDisplay(CategoryBase):
    category_id: int


class ProductBase(BaseModel):
    product_name: str
    category_id: int
    unit: int
    price: float

    class Config:
        orm_mode = True

class ProductDisplay(ProductBase):
    category: Optional[CategoryBase]


class OrderDetailBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class OrderDetailDisplay(OrderDetailBase):
    order_detail_id: int
    product: Optional[ProductDisplay]


class OrderWithDetails(BaseModel):
    order_id: int
    customer_id: int
    order_date: datetime
    order_details: List[OrderDetailDisplay]

    class Config:
        orm_mode = True


class OrderedProduct(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class OrderPlace(BaseModel):
    products: List[OrderedProduct]

    class Config:
        orm_mode = True

class OrderedProductDisplay(BaseModel):
    product_id: int
    quantity: int
    product_name: str
    price: float

    class Config:
        orm_mode = True

class OrderPlaceDisplay(BaseModel):
    order_id: int
    order_date: datetime
    address: str
    products: List[OrderedProductDisplay]
    Total_Amount_to_pay: float

    class Config:
        orm_mode = True

class OrderDisplayForAdmin(BaseModel):
    order_id: int
    order_date: datetime
    customer_id : int
    customer_name : str
    address: str
    products: List[OrderedProductDisplay]
    Total_Amount_to_pay: float

    class Config:
        orm_mode = True

class OrderCancelResponse(BaseModel):
    message: str
    status: str
    
    
class AddTOCart(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True


        
class CartProductDisplay(BaseModel):
    cart_detail_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int

    class Config:
        orm_mode = True
        
class CartProductOut(BaseModel):
    cart_detail_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int

    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    cart_items: List[CartProductOut]

    class Config:
        orm_mode = True
        
class EditCartItem(BaseModel):
    product_id: int
    quantity: int
    
class ProductInOrder(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

    class Config:
        orm_mode = True

class OrderSummary(BaseModel):
    order_id: int
    order_date: datetime
    total_amount: float
    products: List[ProductInOrder]

    class Config:
        orm_mode = True

class PastOrdersResponse(BaseModel):
    past_orders: List[OrderSummary]

    class Config:
        orm_mode = True
        
class ProductOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

class SingleOrderResponse(BaseModel):
    order_id: int
    order_date: datetime
    total_amount: float
    products: List[ProductOut]