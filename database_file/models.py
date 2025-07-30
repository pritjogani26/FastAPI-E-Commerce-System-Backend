# database_file/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Enum
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database_file.database import Base
import enum

# Enums
class UserRoleEnum(enum.Enum):
    admin = "admin"
    employee = "employee"
    customer = "customer"

class OrderStatusEnum(enum.Enum):
    pending = "pending"
    placed = "placed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class CartStatusEnum(enum.Enum):
    active = "active"
    checked_out = "checkedOut"


class Categories(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    listed_time = Column(DateTime(timezone=True), default=func.now())

    products = relationship("Products", back_populates="category", cascade="all, delete")


class Users(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_login = Column(DateTime(timezone=True), default=func.now())
    password = Column(String, nullable=False)
    active_status = Column(Boolean, nullable=False)

    orders = relationship("Orders", back_populates="customer", cascade="all, delete")
    cart_items = relationship("Cart", back_populates="customer", cascade="all, delete")
    addresses = relationship("Address", back_populates="user", cascade="all, delete")


class Address(Base):
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    address_type = Column(String, nullable=False, default="Home")
    address_line_1 = Column(String, nullable=False)
    address_line_2 = Column(String, default="")
    area = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(Integer, nullable=False)

    user = relationship("Users", back_populates="addresses")


class Products(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    unit = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    listed_time = Column(DateTime(timezone=True), default=func.now())

    category = relationship("Categories", back_populates="products")
    order_details = relationship("OrderDetails", back_populates="product", cascade="all, delete")
    cart_details = relationship("CartDetails", back_populates="product", cascade="all, delete")


class Orders(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, unique=True)
    customer_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    order_date = Column(DateTime(timezone=True), default=func.now())
    address = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending, nullable=False)

    # Relationships
    customer = relationship("Users", back_populates="orders")
    order_details = relationship("OrderDetails", back_populates="order", cascade="all, delete")
    payment = relationship("Payments", uselist=False, back_populates="order", cascade="all, delete", passive_deletes=True)


class Payments(Base):
    __tablename__ = "payments"

    payment_id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    order = relationship("Orders", back_populates="payment")


class OrderDetails(Base):
    __tablename__ = 'order_details'

    order_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Orders", back_populates="order_details")
    product = relationship("Products", back_populates="order_details")


class Cart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    session_id = session_id = Column(String, index=True, nullable=True)
    status = Column(Enum(CartStatusEnum), default=CartStatusEnum.active, nullable=False)

    customer = relationship("Users", back_populates="cart_items")
    cart_details = relationship("CartDetails", back_populates="cart", cascade="all, delete")


class CartDetails(Base):
    __tablename__ = "cart_details"

    cart_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.cart_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), default=func.now())

    cart = relationship("Cart", back_populates="cart_details")
    product = relationship("Products", back_populates="cart_details")