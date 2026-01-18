# ------------------------------------------------------------------
#  tests/test_models.py
# ------------------------------------------------------------------
"""
Tests for data models.

Tests cover:
- Model creation and validation
- Relationships between models
- Database operations
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import User, Product, Order, OrderItem

def test_user_creation(session):
    """Test basic user model functionality."""
    # Test valid user creation
    user = User(name="Test User", email="test@example.com")
    session.add(user)
    session.commit()

    assert user.id == 1
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.is_active is True

def test_user_unique_email(session):
    """Test that email must be unique."""
    user1 = User(name="User 1", email="unique@example.com")
    user2 = User(name="User 2", email="unique@example.com")

    session.add(user1)
    session.commit()

    with pytest.raises(IntegrityError):
        session.add(user2)
        session.commit()

def test_product_creation(session):
    """Test product model functionality."""
    product = Product(
        name="Test Product",
        price=9.99,
        stock_quantity=10
    )
    session.add(product)
    session.commit()

    assert str(product.price) == "9.99"
    assert product.stock_quantity == 10

def test_order_relationships(session, sample_data):
    """Test relationships between models."""
    user = sample_data["users"][0]
    orders = user.orders
    assert len(orders) == 1
    assert orders[0].user_id == user.id

    product = sample_data["products"][0]
    order_items = product.order_items
    assert len(order_items) == 1
    assert order_items[0].product_id == product.id

def test_order_item_cascade(session):
    """Test that deleting an order deletes its items."""
    user = User(name="Cascade Test", email="cascade@example.com")
    product = Product(name="Cascade Product", price=5.99)
    order = Order(user=user, total_amount=5.99)

    session.add_all([user, product, order])
    session.commit()

    # Add an item to the order
    item = OrderItem(
        order=order,
        product=product,
        quantity=1,
        unit_price=5.99
    )
    session.add(item)
    session.commit()

    # Verify item exists
    assert len(order.order_items) == 1

    # Delete order and check cascade
    session.delete(order)
    session.commit()

    # Item should be deleted due to cascade
    remaining_items = session.query(OrderItem).filter_by(product_id=product.id).all()
    assert len(remaining_items) == 0

def test_product_stock_management(session):
    """Test product inventory tracking."""
    product = Product(name="Inventory Test", price=1.99, stock_quantity=5)
    session.add(product)
    session.commit()

    # Simulate sale
    product.stock_quantity -= 2
    session.commit()
    session.refresh(product)

    assert product.stock_quantity == 3

def test_order_status_default(session):
    """Test that order status defaults to 'pending'."""
    user = User(name="Status Test", email="status@example.com")
    order = Order(user=user, total_amount=10.0)
    session.add_all([user, order])
    session.commit()

    assert order.status == "pending"
