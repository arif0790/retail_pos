# ------------------------------------------------------------------
#  tests/test_views.py
# ------------------------------------------------------------------
"""
Tests for view functions.

Tests cover:
- Dashboard rendering
- Report generation
- Data formatting
"""

from src.views import render_dashboard, display_report
from src.models import User, Product, Order, OrderItem

def test_render_dashboard_empty(session):
    """Test dashboard with no data."""
    result = render_dashboard()

    assert result["total_users"] == 0
    assert result["total_orders"] == 0
    assert result["revenue"] == 0.0
    assert len(result["top_products"]) == 0

def test_render_dashboard_with_data(session, sample_data):
    """Test dashboard with sample data."""
    result = render_dashboard()

    assert result["total_users"] == 2
    assert result["total_orders"] == 1  # Only completed orders counted
    assert result["revenue"] == 999.99
    assert len(result["top_products"]) == 1

def test_display_report_single_order(session, sample_data):
    """Test displaying a single order."""
    order = sample_data["orders"][0]
    result = display_report(order.id)

    assert result["order_id"] == order.id
    assert result["user_name"] == "John Doe"
    assert result["status"] == "completed"
    assert len(result["items"]) == 1

def test_display_report_nonexistent_order(session):
    """Test displaying a non-existent order."""
    result = display_report(999)
    assert "error" in result
    assert result["error"] == "Order not found"

def test_display_report_summary(session, sample_data):
    """Test displaying summary of all orders."""
    result = display_report()

    assert "total_completed_orders" in result
    assert result["total_completed_orders"] == 1

    # Should have recent orders (last 5)
    assert len(result["recent_orders"]) <= 5

def test_dashboard_calculations(session, sample_data):
    """Test that dashboard calculations are correct."""
    result = render_dashboard()

    # Verify revenue calculation
    assert abs(result["revenue"] - 999.99) < 0.01

    # Verify top products (should be laptop)
    if result["top_products"]:
        assert result["top_products"][0]["name"] == "Laptop"

def test_report_quantity_calculation(session, sample_data):
    """Test that report correctly shows quantities."""
    order = sample_data["orders"][1]  # Pending order with mouse
    result = display_report(order.id)

    # Should show 2 mice at $19.99 each
    assert len(result["items"]) == 1
    assert result["items"][0]["quantity"] == 2
    assert abs(result["items"][0]["price"] - 19.99) < 0.01

def test_dashboard_with_multiple_orders(session):
    """Test dashboard with multiple orders."""
    # Add more data
    user = User(name="Multi Test", email="multi@example.com")
    product = Product(name="Widget", price=4.99, stock_quantity=20)

    order1 = Order(user=user, total_amount=4.99, status="completed")
    order_item1 = OrderItem(order=order1, product=product, quantity=1, unit_price=4.99)

    order2 = Order(user=user, total_amount=9.98, status="completed")
    order_item2 = OrderItem(order=order2, product=product, quantity=2, unit_price=4.99)

    session.add_all([user, product, order1, order2, order_item1, order_item2])
    session.commit()

    result = render_dashboard()

    assert result["total_orders"] == 3
    assert abs(result["revenue"] - (999.99 + 4.99 + 9.98)) < 0.01

    # Widget should be in top products
    widget_in_top = any(p["name"] == "Widget" for p in result["top_products"])
    assert widget_in_top
