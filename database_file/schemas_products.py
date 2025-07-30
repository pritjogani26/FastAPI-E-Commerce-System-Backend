# database_file/schemas_products.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True
    }

# Category-------------------------------------------------------------------------------------------------------
class AddCategory(BaseSchema):
    category_name: str
    description: str
 
class DisplayCategory(BaseSchema):
    category_id: int
    category_name: str
    description: str
    listed_time: datetime

# Product-------------------------------------------------------------------------------------------------------
class AddProduct(BaseSchema):
    product_name: str
    category_id: int
    unit: int
    price: float  

class DisplayProduct(BaseSchema):
    product_id: int
    product_name: str
    unit: int
    price: float
    listed_time: datetime
    category: Optional[AddCategory] = []

# Create Order-------------------------------------------------------------------------------------------------------

class OrderProductInput(BaseSchema):
    product_id: int
    quantity: int

class OrderCreateSingle(OrderProductInput):
    address_id: Optional[int]

class OrderCreateMultiple(BaseSchema):
    address_id: Optional[int]
    products: List[OrderProductInput]

# Display Order-------------------------------------------------------------------------------------------------------

class OrderedProductDisplay(BaseSchema):
    product_name: str
    price: float
    quantity: int
    subtotal: float 
        
class OrderDisplay(BaseSchema):
    order_id: str
    customer_id : str
    customer_name : Optional[str]
    order_date: datetime
    address: str
    status: Optional[str]
    total_amount: float
    products: List[OrderedProductDisplay]

class PastOrdersDisplay(BaseSchema):
    past_orders: List[OrderDisplay]

class OrderDisplayForAdmin(BaseSchema):
    order_id: str
    customer_id: str
    order_date: datetime
    address: str
    status: str
    total_amount: float
    products: List[OrderedProductDisplay]

# Cart-------------------------------------------------------------------------------------------------------

class CartProductOut(BaseSchema):
    cart_detail_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
     
class EditCartItem(BaseSchema):
    product_id: int
    quantity: int