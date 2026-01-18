
"""
POS Application Main Entry Point

This script initializes and runs the Point of Sale application.
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from .src.models import SessionLocal
from .src.models import Base
from .src.models import User
from .src.models import Product
from .src.models import Order
from .src.models import OrderItem
from .src.views import render_dashboard
from .src.views import display_report
from .src.utils import init_db, seed_database
from .src.utils import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class POSApplication:
    """Main application class for the POS system."""

    def __init__(self):
        """Initialize the POS application."""
        self.config = load_config()
        self.db_session: Optional[SessionLocal] = None
        logger.info("POS Application initialized")

    def initialize_database(self) -> None:
        """Initialize and seed the database."""
        try:
            init_db()
            if self.config.get('SEED_DATA', False):
                seed_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_db_session(self) -> SessionLocal:
        """Get a database session."""
        if not self.db_session:
            self.db_session = SessionLocal()
        return self.db_session

    def close_db_session(self) -> None:
        """Close the database session."""
        if self.db_session:
            self.db_session.close()
            self.db_session = None

    def show_main_menu(self) -> None:
        """Display the main application menu."""
        print("\n" + "="*50)
        print("POS SYSTEM - MAIN MENU".center(50))
        print("="*50)
        print("1. View Dashboard")
        print("2. Manage Products")
        print("3. Process Sale")
        print("4. Generate Reports")
        print("5. Manage Users")
        print("6. Settings")
        print("7. Exit")
        print("-"*50)

    def handle_product_management(self) -> None:
        """Handle product management operations."""
        while True:
            self.show_product_menu()
            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                self.list_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.update_product()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def show_product_menu(self) -> None:
        """Display product management menu."""
        print("\n" + "="*50)
        print("PRODUCT MANAGEMENT".center(50))
        print("="*50)
        print("1. List All Products")
        print("2. Add New Product")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Back to Main Menu")
        print("-"*50)

    def list_products(self) -> None:
        """List all products in the database."""
        try:
            session = self.get_db_session()
            products = session.query(Product).all()

            if not products:
                print("\nNo products found.")
                return

            print("\n" + "="*70)
            print("PRODUCT LIST".center(70))
            print("="*70)
            print(f"{'ID':<5} {'Name':<25} {'Price':<10} {'Stock':<8}")
            print("-"*70)

            for product in products:
                print(f"{product.id:<5} {product.name:<25} ${product.price:<9.2f} {product.stock_quantity:<8}")

            print("="*70)
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            print("Error occurred while fetching products.")

    def add_product(self) -> None:
        """Add a new product to the inventory."""
        try:
            session = self.get_db_session()

            name = input("\nEnter product name: ").strip()
            if not name:
                print("Product name cannot be empty.")
                return

            try:
                price = float(input("Enter product price: ").strip())
                if price <= 0:
                    print("Price must be positive.")
                    return
            except ValueError:
                print("Invalid price. Please enter a number.")
                return

            try:
                stock = int(input("Enter initial stock quantity: ").strip())
                if stock < 0:
                    print("Stock quantity cannot be negative.")
                    return
            except ValueError:
                print("Invalid stock quantity. Please enter an integer.")
                return

            # Check if product already exists
            existing = session.query(Product).filter_by(name=name).first()
            if existing:
                print(f"Product '{name}' already exists!")
                return

            new_product = Product(
                name=name,
                price=price,
                stock_quantity=stock
            )

            session.add(new_product)
            session.commit()
            logger.info(f"Added new product: {name}")
            print(f"\nProduct '{name}' added successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding product: {e}")
            print("Failed to add product.")

    def update_product(self) -> None:
        """Update an existing product."""
        try:
            self.list_products()

            product_id = input("\nEnter the ID of the product to update: ").strip()
            if not product_id.isdigit():
                print("Invalid product ID.")
                return

            session = self.get_db_session()
            product = session.query(Product).get(int(product_id))

            if not product:
                print("Product not found.")
                return

            print(f"\nUpdating product: {product.name}")
            print(f"Current price: ${product.price:.2f}")
            print(f"Current stock: {product.stock_quantity}")

            action = input("\nWhat would you like to update?\n"
                          "1. Name\n"
                          "2. Price\n"
                          "3. Stock Quantity\n"
                          "4. Cancel\n"
                          "Enter choice (1-4): ").strip()

            if action == '1':
                new_name = input("Enter new name: ").strip()
                if not new_name:
                    print("Name cannot be empty.")
                    return

                # Check for duplicate names
                existing = session.query(Product).filter(
                    Product.name == new_name,
                    Product.id != product.id
                ).first()

                if existing:
                    print(f"Product with name '{new_name}' already exists!")
                    return

                product.name = new_name
                logger.info(f"Updated product {product.id} name to: {new_name}")

            elif action == '2':
                try:
                    new_price = float(input("Enter new price: ").strip())
                    if new_price <= 0:
                        print("Price must be positive.")
                        return
                    product.price = new_price
                    logger.info(f"Updated product {product.id} price to: ${new_price:.2f}")
                except ValueError:
                    print("Invalid price. Update canceled.")
                    return

            elif action == '3':
                try:
                    new_stock = int(input("Enter new stock quantity: ").strip())
                    if new_stock < 0:
                        print("Stock cannot be negative.")
                        return
                    product.stock_quantity = new_stock
                    logger.info(f"Updated product {product.id} stock to: {new_stock}")
                except ValueError:
                    print("Invalid stock quantity. Update canceled.")
                    return

            elif action == '4':
                print("Update canceled.")
                return

            else:
                print("Invalid choice.")
                return

            session.commit()
            print(f"\nProduct '{product.name}' updated successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating product: {e}")
            print("Failed to update product.")

    def delete_product(self) -> None:
        """Delete a product from inventory."""
        try:
            self.list_products()

            product_id = input("\nEnter the ID of the product to delete: ").strip()
            if not product_id.isdigit():
                print("Invalid product ID.")
                return

            session = self.get_db_session()
            product = session.query(Product).get(int(product_id))

            if not product:
                print("Product not found.")
                return

            confirm = input(f"Are you sure you want to delete '{product.name}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion canceled.")
                return

            # Check if product is in any orders
            order_items = session.query(OrderItem).filter_by(product_id=product.id).all()
            if order_items:
                print(f"Cannot delete product. It's referenced in {len(order_items)} order(s).")
                return

            session.delete(product)
            session.commit()
            logger.info(f"Deleted product: {product.name}")
            print(f"\nProduct '{product.name}' deleted successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting product: {e}")
            print("Failed to delete product.")

    def process_sale(self) -> None:
        """Process a new sale transaction."""
        try:
            session = self.get_db_session()

            # Get active user (simplified - in real app would get current user)
            user = session.query(User).first()
            if not user:
                print("No users found. Please add a user first.")
                return

            print("\n" + "="*50)
            print("PROCESS NEW SALE".center(50))
            print("="*50)

            # List available products
            self.list_products()

            items: List[Dict[str, Any]] = []
            total = 0.0

            while True:
                product_id = input("\nEnter product ID to add (or 'done' to finish): ").strip()
                if product_id.lower() == 'done':
                    break
                elif not product_id.isdigit():
                    print("Invalid input. Please enter a number or 'done'.")
                    continue

                product = session.query(Product).get(int(product_id))
                if not product:
                    print("Product not found.")
                    continue

                try:
                    quantity = int(input(f"Enter quantity for {product.name}: ").strip())
                    if quantity <= 0:
                        print("Quantity must be positive.")
                        continue
                    elif quantity > product.stock_quantity:
                        print(f"Not enough stock. Only {product.stock_quantity} available.")
                        continue

                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'unit_price': product.price
                    })

                    total += product.price * quantity
                    print(f"Added {quantity} x {product.name} to sale (${product.price:.2f} each)")

                except ValueError:
                    print("Invalid quantity. Please enter a number.")
                    continue

            if not items:
                print("No items added to sale.")
                return

            # Display order summary
            print("\n" + "="*50)
            print("ORDER SUMMARY".center(50))
            print("="*50)
            print(f"{'Product':<25} {'Quantity':<10} {'Price':<10}")
            print("-"*50)

            for item in items:
                print(f"{item['product'].name:<25} {item['quantity']:<10} ${item['unit_price']:<9.2f}")

            print("-"*50)
            print(f"{"Total":<35} ${total:.2f}")
            print("="*50)

            confirm = input("\nConfirm sale? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Sale canceled.")
                return

            # Create order
            order = Order(
                user_id=user.id,
                total_amount=total,
                status='completed'
            )

            session.add(order)
            session.commit()

            # Add order items and update stock
            for item in items:
                product = item['product']
                quantity = item['quantity']

                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price
                )

                session.add(order_item)

                # Update product stock
                product.stock_quantity -= quantity

            session.commit()
            logger.info(f"Processed sale #{order.id} for ${total:.2f}")
            print(f"\nSale completed! Order ID: {order.id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error processing sale: {e}")
            print("Failed to process sale.")

    def generate_reports(self) -> None:
        """Generate various reports."""
        while True:
            self.show_report_menu()
            choice = input("Enter your choice (1-4): ").strip()

            if choice == '1':
                self.daily_sales_report()
            elif choice == '2':
                self.product_inventory_report()
            elif choice == '3':
                self.customer_purchases_report()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def show_report_menu(self) -> None:
        """Display report generation menu."""
        print("\n" + "="*50)
        print("REPORT GENERATION".center(50))
        print("="*50)
        print("1. Daily Sales Report")
        print("2. Product Inventory Report")
        print("3. Customer Purchases Report")
        print("4. Back to Main Menu")
        print("-"*50)

    def daily_sales_report(self) -> None:
        """Generate a report of sales for the current day."""
        try:
            session = self.get_db_session()
            today = datetime.now().date()

            # Get completed orders from today
            orders = session.query(Order).filter(
                Order.status == 'completed',
                datetime.fromtimestamp(Order.created_at).date() == today
            ).all()

            if not orders:
                print("\nNo sales recorded for today.")
                return

            total_sales = sum(order.total_amount for order in orders)
            avg_order_value = total_sales / len(orders)

            print("\n" + "="*70)
            print(f"DAILY SALES REPORT - {today.strftime('%B %d, %Y')}".center(70))
            print("="*70)
            print(f"{"Total Orders":<35} {len(orders):<10}")
            print(f"{"Total Sales":<35} ${total_sales:<9.2f}")
            print(f"{"Average Order Value":<35} ${avg_order_value:<9.2f}")
            print("-"*70)

            # Show top 5 products sold today
            from sqlalchemy import func

            top_products = session.query(
                Product.name,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.unit_price * OrderItem.quantity).label('revenue')
            ).join(
                OrderItem, Product.id == OrderItem.product_id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.status == 'completed',
                datetime.fromtimestamp(Order.created_at).date() == today
            ).group_by(
                Product.name
            ).order_by(
                func.sum(OrderItem.quantity).desc()
            ).limit(5).all()

            if top_products:
                print("\nTop 5 Products Sold Today:")
                print(f"{"Product":<25} {"Quantity":<10} {"Revenue":<10}")
                print("-"*70)

                for product in top_products:
                    print(f"{product.name:<25} {product.total_quantity:<10} ${product.revenue:<9.2f}")

            print("="*70)
        except Exception as e:
            logger.error(f"Error generating daily sales report: {e}")
            print("Failed to generate report.")

    def product_inventory_report(self) -> None:
        """Generate a report of current inventory levels."""
        try:
            session = self.get_db_session()

            products = session.query(Product).all()
            if not products:
                print("\nNo products in inventory.")
                return

            low_stock = [p for p in products if p.stock_quantity < 10]
            out_of_stock = [p for p in products if p.stock_quantity == 0]

            print("\n" + "="*70)
            print("PRODUCT INVENTORY REPORT".center(70))
            print("="*70)
            print(f"{"Product":<25} {"Price":<10} {"In Stock":<8} {"Value":<10}")
            print("-"*70)

            total_value = 0.0
            for product in products:
                value = product.price * product.stock_quantity
                total_value += value
                print(f"{product.name:<25} ${product.price:<9.2f} {product.stock_quantity:<8} ${value:<9.2f}")

            print("-"*70)
            print(f"{"Total Inventory Value":<35} ${total_value:<9.2f}")
            print("="*70)

            if low_stock:
                print("\nLow Stock Items (less than 10):")
                for product in low_stock:
                    print(f"- {product.name}: {product.stock_quantity} remaining")

            if out_of_stock:
                print("\nOut of Stock Items:")
                for product in out_of_stock:
                    print(f"- {product.name}")

        except Exception as e:
            logger.error(f"Error generating inventory report: {e}")
            print("Failed to generate report.")

    def customer_purchases_report(self) -> None:
        """Generate a report of customer purchases."""
        try:
            session = self.get_db_session()

            # Get users with orders
            from sqlalchemy import func

            customers = session.query(
                User.id,
                User.name,
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('total_spent')
            ).join(
                Order, User.id == Order.user_id
            ).group_by(
                User.id
            ).all()

            if not customers:
                print("\nNo customer purchase data available.")
                return

            print("\n" + "="*70)
            print("CUSTOMER PURCHASES REPORT".center(70))
            print("="*70)
            print(f"{"Customer":<25} {"Orders":<10} {"Total Spent":<10}")
            print("-"*70)

            for customer in customers:
                print(f"{customer.name:<25} {customer.order_count:<10} ${customer.total_spent:<9.2f}")

            print("="*70)
        except Exception as e:
            logger.error(f"Error generating customer report: {e}")
            print("Failed to generate report.")

    def manage_users(self) -> None:
        """Manage user accounts."""
        while True:
            self.show_user_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == '1':
                self.list_users()
            elif choice == '2':
                self.add_user()
            elif choice == '3':
                self.update_user()
            elif choice == '4':
                self.delete_user()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def show_user_menu(self) -> None:
        """Display user management menu."""
        print("\n" + "="*50)
        print("USER MANAGEMENT".center(50))
        print("="*50)
        print("1. List All Users")
        print("2. Add New User")
        print("3. Update User")
        print("4. Delete User")
        print("5. Back to Main Menu")
        print("-"*50)

    def list_users(self) -> None:
        """List all users in the system."""
        try:
            session = self.get_db_session()
            users = session.query(User).all()

            if not users:
                print("\nNo users found.")
                return

            print("\n" + "="*70)
            print("USER LIST".center(70))
            print("="*70)
            print(f"{"ID":<5} {"Name":<25} {"Email":<30} {"Active":<8}")
            print("-"*70)

            for user in users:
                status = "Yes" if user.is_active else "No"
                print(f"{user.id:<5} {user.name:<25} {user.email:<30} {status:<8}")

            print("="*70)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            print("Error occurred while fetching users.")

    def add_user(self) -> None:
        """Add a new user to the system."""
        try:
            session = self.get_db_session()

            name = input("\nEnter full name: ").strip()
            if not name:
                print("Name cannot be empty.")
                return

            email = input("Enter email address: ").strip()
            if not email or '@' not in email:
                print("Valid email is required.")
                return

            # Check for duplicate email
            existing = session.query(User).filter_by(email=email).first()
            if existing:
                print(f"User with email '{email}' already exists!")
                return

            new_user = User(
                name=name,
                email=email,
                is_active=True
            )

            session.add(new_user)
            session.commit()
            logger.info(f"Added new user: {name} ({email})")
            print(f"\nUser '{name}' added successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding user: {e}")
            print("Failed to add user.")

    def update_user(self) -> None:
        """Update an existing user."""
        try:
            self.list_users()

            user_id = input("\nEnter the ID of the user to update: ").strip()
            if not user_id.isdigit():
                print("Invalid user ID.")
                return

            session = self.get_db_session()
            user = session.query(User).get(int(user_id))

            if not user:
                print("User not found.")
                return

            print(f"\nUpdating user: {user.name}")
            print(f"Current email: {user.email}")
            print(f"Active status: {'Yes' if user.is_active else 'No'}")

            action = input("\nWhat would you like to update?\n"
                          "1. Name\n"
                          "2. Email\n"
                          "3. Active Status\n"
                          "4. Cancel\n"
                          "Enter choice (1-4): ").strip()

            if action == '1':
                new_name = input("Enter new name: ").strip()
                if not new_name:
                    print("Name cannot be empty.")
                    return
                user.name = new_name
                logger.info(f"Updated user {user.id} name to: {new_name}")

            elif action == '2':
                new_email = input("Enter new email: ").strip()
                if not new_email or '@' not in new_email:
                    print("Valid email is required.")
                    return

                # Check for duplicate emails
                existing = session.query(User).filter(
                    User.email == new_email,
                    User.id != user.id
                ).first()

                if existing:
                    print(f"User with email '{new_email}' already exists!")
                    return

                user.email = new_email
                logger.info(f"Updated user {user.id} email to: {new_email}")

            elif action == '3':
                new_status = input("Set active status (y/n): ").strip().lower()
                if new_status == 'y':
                    user.is_active = True
                    logger.info(f"Activated user {user.id}")
                elif new_status == 'n':
                    user.is_active = False
                    logger.info(f"Deactivated user {user.id}")
                else:
                    print("Invalid choice. Status not changed.")
                    return

            elif action == '4':
                print("Update canceled.")
                return

            else:
                print("Invalid choice.")
                return

            session.commit()
            print(f"\nUser '{user.name}' updated successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user: {e}")
            print("Failed to update user.")

    def delete_user(self) -> None:
        """Delete a user from the system."""
        try:
            self.list_users()

            user_id = input("\nEnter the ID of the user to delete: ").strip()
            if not user_id.isdigit():
                print("Invalid user ID.")
                return

            session = self.get_db_session()
            user = session.query(User).get(int(user_id))

            if not user:
                print("User not found.")
                return

            confirm = input(f"Are you sure you want to delete '{user.name}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion canceled.")
                return

            # Check if user has orders
            order_count = session.query(Order).filter_by(user_id=user.id).count()
            if order_count > 0:
                print(f"Cannot delete user. They have {order_count} order(s) associated.")
                return

            session.delete(user)
            session.commit()
            logger.info(f"Deleted user: {user.name}")
            print(f"\nUser '{user.name}' deleted successfully!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting user: {e}")
            print("Failed to delete user.")

    def show_settings(self) -> None:
        """Display application settings."""
        print("\n" + "="*50)
        print("SETTINGS".center(50))
        print("="*50)
        print(f"{"Database":<20} {self.config.get('database', 'N/A')}")
        print(f"{"Log Level":<20} {self.config.get('log_level', 'INFO')}")
        print("-"*50)

    def run(self) -> None:
        """Run the main application loop."""
        try:
            self.initialize()

            while True:
                self.show_main_menu()
                choice = input("Enter your choice (1-6): ").strip()

                if choice == '1':
                    # In a real app, this would show dashboard with key metrics
                    print("\nDashboard functionality would be implemented here.")
                elif choice == '2':
                    self.handle_product_management()
                elif choice == '3':
                    self.process_sale()
                elif choice == '4':
                    self.generate_reports()
                elif choice == '5':
                    self.manage_users()
                elif choice == '6':
                    print("\nThank you for using the POS System. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\nApplication terminated by user.")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print("An unexpected error occurred. Please check the logs for details.")
        finally:
            self.cleanup()

    def show_main_menu(self) -> None:
        """Display the main application menu."""
        print("\n" + "="*50)
        print("POS SYSTEM".center(50))
        print("="*50)
        print("1. Dashboard")
        print("2. Product Management")
        print("3. Process Sale")
        print("4. Generate Reports")
        print("5. User Management")
        print("6. Exit")
        print("-"*50)

    def initialize(self) -> None:
        """Initialize the application."""
        self.config = {
            'database': 'sqlite:///pos.db',
            'log_level': 'INFO'
        }

        # Initialize database
        from src.models import Base
        from sqlalchemy import create_engine

        engine = create_engine(self.config['database'])
        Base.metadata.create_all(engine)

        logger.info("Application initialized successfully")

    def cleanup(self) -> None:
        """Clean up resources before exiting."""
        if hasattr(self, '_session'):
            self._session.close()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    # Configure logging
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pos.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    try:
        app = POSApplication()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print("A fatal error occurred. Check the logs for details.")
