import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
import random
from datetime import datetime, timedelta

# Try Uzbek locale, fallback to default if not available
try:
    fake = Faker('uz_UZ')
except:
    fake = Faker()  # Fallback to default locale

# Realistic product names
PRODUCTS = [
    "Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard", 
    "Mouse", "Headphones", "Speaker", "Camera", "Printer",
    "Router", "Hard Drive", "SSD", "RAM", "Processor",
    "Graphics Card", "Motherboard", "Power Supply", "Cooling Fan", "Webcam"
]

def seed():
    db: Session = SessionLocal()
    
    # Clear existing data (order matters due to foreign keys)
    print("Clearing existing data...")
    try:
        # Delete in correct order to respect foreign key constraints
        db.query(models.Sale).delete()
        db.commit()
        print("  ✓ Sales deleted")
        
        db.query(models.Order).delete()
        db.commit()
        print("  ✓ Orders deleted")
        
        db.query(models.User).delete()
        db.commit()
        print("  ✓ Users deleted")
    except Exception as e:
        print(f"  ⚠ Error clearing data: {e}")
        db.rollback()
        # Try alternative method
        try:
            db.execute("DELETE FROM sales")
            db.execute("DELETE FROM orders")
            db.execute("DELETE FROM users")
            db.commit()
            print("  ✓ Data cleared using raw SQL")
        except Exception as e2:
            print(f"  ❌ Failed to clear data: {e2}")
            db.rollback()

    # Create users with proper first and last names
    print("Creating users...")
    users = []
    for _ in range(150):
        # Generate proper name with first and last name
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        user = models.User(
            name=full_name,
            email=fake.unique.email()
        )
        db.add(user)
        users.append(user)
    db.commit()
    print(f"Created {len(users)} users")

    # Create orders with realistic products
    print("Creating orders...")
    orders = []
    
    # Create orders with specific products and amounts
    product_distribution = {
        "Laptop": (50, 800, 2000),      # 50 orders, $800-$2000
        "Smartphone": (80, 300, 1200),   # 80 orders, $300-$1200
        "Tablet": (40, 200, 800),        # 40 orders, $200-$800
        "Monitor": (60, 150, 600),       # 60 orders, $150-$600
        "Keyboard": (70, 20, 200),       # 70 orders, $20-$200
        "Mouse": (80, 10, 100),          # 80 orders, $10-$100
        "Headphones": (60, 50, 400),     # 60 orders, $50-$400
        "Speaker": (50, 80, 500),        # 50 orders, $80-$500
        "Camera": (40, 300, 1500),       # 40 orders, $300-$1500
        "Printer": (30, 100, 800),       # 30 orders, $100-$800
        "Router": (40, 50, 300),         # 40 orders, $50-$300
        "Hard Drive": (50, 60, 300),     # 50 orders, $60-$300
        "SSD": (50, 80, 500),            # 50 orders, $80-$500
        "RAM": (50, 40, 400),            # 50 orders, $40-$400
        "Processor": (30, 200, 800),      # 30 orders, $200-$800
        "Graphics Card": (25, 300, 2000), # 25 orders, $300-$2000
        "Motherboard": (20, 100, 500),    # 20 orders, $100-$500
        "Power Supply": (25, 50, 300),    # 25 orders, $50-$300
        "Cooling Fan": (30, 20, 150),     # 30 orders, $20-$150
        "Webcam": (40, 30, 200)          # 40 orders, $30-$200
    }
    
    # Generate orders based on distribution
    for product, (count, min_price, max_price) in product_distribution.items():
        for _ in range(count):
            user = random.choice(users)
            # Random date within last 6 months
            days_ago = random.randint(0, 180)
            order_date = datetime.utcnow() - timedelta(days=days_ago)
            
            order = models.Order(
                user_id=user.id,
                product=product,
                amount=round(random.uniform(min_price, max_price), 2),
                created_at=order_date
            )
            db.add(order)
            orders.append(order)
    
    # Add some random orders with other products
    for _ in range(100):
        user = random.choice(users)
        product = random.choice(PRODUCTS)
        days_ago = random.randint(0, 180)
        order_date = datetime.utcnow() - timedelta(days=days_ago)
        
        order = models.Order(
            user_id=user.id,
            product=product,
            amount=round(random.uniform(10, 500), 2),
            created_at=order_date
        )
        db.add(order)
        orders.append(order)
    
    db.commit()
    print(f"Created {len(orders)} orders")

    # Create sales (revenue is typically higher than order amount)
    print("Creating sales...")
    sales = []
    for order in orders:
        # 70% chance that an order has a sale
        if random.random() < 0.7:
            # Revenue is order amount + 10-50% markup
            revenue = round(order.amount * random.uniform(1.1, 1.5), 2)
            # Sale date is same or slightly after order date
            sale_date = order.created_at + timedelta(days=random.randint(0, 7))
            
            sale = models.Sale(
                order_id=order.id,
                revenue=revenue,
                created_at=sale_date
            )
            db.add(sale)
            sales.append(sale)
    
    db.commit()
    print(f"Created {len(sales)} sales")
    
    db.close()
    print("\n✅ Data seeded successfully!")
    print(f"📊 Summary:")
    print(f"   - Users: {len(users)}")
    print(f"   - Orders: {len(orders)}")
    print(f"   - Sales: {len(sales)}")
    print(f"   - Products: {len(set(order.product for order in orders))} unique products")


if __name__ == "__main__":
    seed()