# # database_file/schemas_users.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True
    }

#-----------Login----------------

class LoginRequest(BaseSchema):
    email : str
    password : str


# -------- Address Schemas --------
class AddressBase(BaseSchema):
    address_type: str
    address_line_1: str
    address_line_2: Optional[str] = ""
    area: str
    city: str
    state: str
    pincode: int

class AddressCreate(AddressBase):
    customer_id: str  # Foreign key reference


class AddressDisplay(AddressBase):
    address_id: int
    
# -------- User Schemas --------
class LoginUser(BaseSchema):
    email: EmailStr
    password: str

class RegisterUser(BaseSchema):
    name: str
    email: EmailStr
    password: str
    role: str
    address: AddressBase

class DisplayUser(BaseSchema):
    user_id: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    last_login: datetime
    active_status: bool
    addresses: List[AddressDisplay] = [] 

class FullUser(BaseSchema):
    user_id: str
    name: str
    email: EmailStr
    role: str
    password: str  
    created_at: datetime
    last_login: datetime
    active_status: bool
    addresses: List[AddressDisplay] = []

class UpdateUser(BaseSchema):
    name: Optional[str]
    role: Optional[str]

class Token(BaseSchema):
    access_token : str
    token_type : str
    
class TokenData(BaseSchema):
    email: Optional[str] = None
    
