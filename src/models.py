# ------------------------------------------------------------------
#  src/models.py
# ------------------------------------------------------------------
"""
Core database models for the POS Application.

This module defines the three main entities:
- User: Represents customers or staff who interact with the system.
- Product: Items available for sale in the inventory.
- Order: Transactions that link users to products with quantities and prices.

All models use SQLAlchemy ORM for database operations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///db.sqlite3")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ------------------------------------------------------------------
#  Base class for all models (SQLAlchemy 2.0 style)
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class that provides common functionality to all models."""
    pass

# ------------------------------------------------------------------
#  User Model
# ------------------------------------------------------------------
class User(Base):
    """
    Represents a user in the system (customer or staff).

    Attributes:
        id: Primary key
        name: Full name of the user
        email: Contact email (unique)
        is_active: Whether the account is active
        created_at: Timestamp when record was created
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationship to orders (one-to-many)
    orders: Mapped[List["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}' email='{self.email}'>"

# ------------------------------------------------------------------
#  Product Model
# ------------------------------------------------------------------
class Product(Base):
    """
    Represents an item in inventory that can be sold.

    Attributes:
        id: Primary key
        name: Product name
        price: Current selling price
        stock_quantity: Available quantity
        created_at: Timestamp when record was created
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Float, default=0)
    stock_unit: Mapped[int] = mapped_column(String(20), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationship to orders (many-to-many via OrderItem)
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.name}' price={self.price}>"

# ------------------------------------------------------------------
#  Order Model
# ------------------------------------------------------------------
class Order(Base):
    """
    Represents a transaction in the POS system.

    Attributes:
        id: Primary key
        user_id: Foreign key to User (who placed the order)
        total_amount: Sum of all items in this order
        status: Current state ('pending', 'completed', etc.)
        created_at: Timestamp when order was placed
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to user (many-to-one)
    user: Mapped["User"] = relationship(
        back_populates="orders"
    )

    # Relationship to order items (one-to-many)
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} user_id={self.user_id} total={self.total_amount}>"

# ------------------------------------------------------------------
#  OrderItem Model (Join Table)
# ------------------------------------------------------------------
class OrderItem(Base):
    """
    Join table between Order and Product to handle quantities.

    Attributes:
        order_id: Foreign key to Order
        product_id: Foreign key to Product
        quantity: Number of this product in the order
        unit_price: Price at time of purchase (may differ from current price)
    """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Float)

    # Relationships
    order: Mapped["Order"] = relationship(
        back_populates="order_items"
    )
    product: Mapped["Product"] = relationship(
        back_populates="order_items"
    )

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} order_id={self.order_id} product_id={self.product_id}>"

# ------------------------------------------------------------------
#  Helper functions for database operations
# ------------------------------------------------------------------
def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)

def get_session(engine):
    """Get a new SQLAlchemy session."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()
