from math import factorial
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.testing.suite.test_reflection import users

from app.db.database import SessionLocal,engine
from app.db import models
import random

fake = Faker()

def seed():
    db: Session = SessionLocal()

    users = []
    for _ in range(150):
        user = models.User(name=fake.name(),email=fake.unique.email())
        db.add(user)
        users.append(user)
    db.commit()

    orders = []
    for _ in range(600):
        user = random.choice(users)
        order = models.Order(
            user_id=user.id,
            product=fake.word(),
            amount=round(random.uniform(10, 500), 2)
        )
        db.add(order)
        orders.append(order)
    db.commit()

    # 250 sales
    for _ in range(750):
        order = random.choice(orders)
        sale = models.Sale(order_id=order.id, revenue=order.amount * random.uniform(1.1, 1.5))
        db.add(sale)
    db.commit()
    db.close()
    print("Data seeded!")


if __name__ == "__main__":
    seed()