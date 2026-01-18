# ------------------------------------------------------------------
#  tests/conftest.py
# ------------------------------------------------------------------
"""
Pytest configuration and shared fixtures.

This file contains:
- Test database setup/teardown
- Sample data creation
- Common test utilities
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, User, Product, Order, OrderItem, get_session
from src.utils import db_connect

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create and return a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)  # Create tables
    yield engine
    Base.metadata.drop_all(engine)  # Clean up

@pytest.fixture
def session(engine):
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_data(session):
    """Create and return sample data for testing."""
    # Create users
    user1 = User(name="John Doe", email="john@example.com")
    user2 = User(name="Jane Smith", email="jane@example.com")

    # Create products
    product1 = Product(name="Laptop", price=999.99, stock_quantity=10)
    product2 = Product(name="Mouse", price=19.99, stock_quantity=50)

    # Create orders
    order1 = Order(user=user1, total_amount=999.99, status="completed")
    order_item1 = OrderItem(
        order=order1,
        product=product1,
        quantity=1,
        unit_price=999.99
    )

    order2 = Order(user=user2, total_amount=39.98, status="pending")
    order_item2 = OrderItem(
        order=order2,
        product=product2,
        quantity=2,
        unit_price=19.99
    )

    session.add_all([
        user1, user2,
        product1, product2,
        order1, order2,
        order_item1, order_item2
    ])
    session.commit()

    return {
        "users": [user1, user2],
        "products": [product1, product2],
        "orders": [order1, order2]
    }

@pytest.fixture(autouse=True)
def mock_db_connect(session):
    """Mock db_connect to use test session."""
    import src.utils
    original_func = src.utils.db_connect

    def mock_func():
        return session

    src.utils.db_connect = mock_func
    yield
    src.utils.db_connect = original_func
