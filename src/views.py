# ------------------------------------------------------------------
#  src/views.py
# ------------------------------------------------------------------
"""
View layer for the POS Application.

This module contains functions responsible for displaying data to users.
Currently implements two main views:
- render_dashboard: Main interface showing key metrics
- display_report: Detailed transaction reports

Both functions interact with models to fetch and format data.
"""

from typing import List, Dict, Any
import logging

from .models import User, Order, Product, get_session, OrderItem
from sqlalchemy.orm import Session

# Get logger from utils (circular import avoided via late binding)
logger = None  # Will be set in __init__.py or at runtime

def render_dashboard() -> Dict[str, Any]:
    """
    Renders the main dashboard with key POS metrics.

    Returns:
        Dictionary containing:
            - total_users: Number of active users
            - total_orders: Number of completed orders
            - revenue: Total revenue from all orders
            - top_products: List of 5 best-selling products

    Example usage:
        >>> dashboard_data = render_dashboard()
        >>> print(f"Total Revenue: ${dashboard_data['revenue']:.2f}")
    """
    try:
        session: Session = get_session()  # Get DB session from utils
        logger.info("Rendering dashboard view")

        # Fetch key metrics
        total_users = session.query(User).filter_by(is_active=True).count()
        total_orders = session.query(Order).filter_by(status="completed").count()

        revenue_query = (
            session.query(
                Order.total_amount
            ).filter(
                Order.status == "completed"
            ).all()
        )
        revenue = sum(order[0] for order in revenue_query)

        # Get top 5 products by quantity sold
        top_products = (
            session.query(
                Product.name,
                Product.price,
                OrderItem.quantity
            )
            .join(OrderItem)
            .group_by(Product.id)
            .order_by("quantity desc")
            .limit(5)
            .all()
        )

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "revenue": revenue,
            "top_products": [
                {"name": p[0], "price": p[1], "quantity_sold": p[2]}
                for p in top_products
            ]
        }

    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        raise

def display_report(order_id: int = None) -> Dict[str, Any]:
    """
    Displays detailed report for a specific order or all orders.

    Args:
        order_id: Optional ID of specific order to display.
                 If None, returns summary of all orders.

    Returns:
        Dictionary containing order details or summary statistics.

    Example usage:
        >>> single_order = display_report(42)
        >>> all_orders = display_report()
    """
    try:
        session: Session = get_session()
        logger.info(f"Displaying report for order_id={order_id}")

        if order_id is not None:
            # Single order details
            order = session.query(Order).get(order_id)
            if not order:
                return {"error": "Order not found"}

            items = (
                session.query(
                    Product.name,
                    OrderItem.quantity,
                    OrderItem.unit_price
                )
                .join(Product)
                .filter(OrderItem.order_id == order_id)
                .all()
            )

            return {
                "order_id": order.id,
                "user_name": order.user.name,
                "status": order.status,
                "total_amount": order.total_amount,
                "items": [
                    {"product": item[0], "quantity": item[1], "price": item[2]}
                    for item in items
                ]
            }

        else:
            # Summary of all orders
            completed_orders = session.query(Order).filter_by(status="completed").all()
            return {
                "total_completed_orders": len(completed_orders),
                "average_order_value": (
                    sum(o.total_amount for o in completed_orders) / len(completed_orders)
                    if completed_orders else 0
                ),
                "recent_orders": [
                    {"id": o.id, "user": o.user.name, "amount": o.total_amount}
                    for o in sorted(completed_orders, key=lambda x: x.created_at)[-5:]
                ]
            }

    except Exception as e:
        logger.error(f"Error displaying report: {str(e)}")
        raise
