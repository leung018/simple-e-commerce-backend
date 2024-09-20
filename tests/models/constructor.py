from app.models.auth import AuthInput, AuthRecord
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User


def new_order(
    id="o1",
    user_id="u1",
    order_items=(
        OrderItem(product_id="p1", quantity=2),
        OrderItem(product_id="p2", quantity=3),
    ),
):
    return Order(id, user_id, order_items)


def new_product(id="p1", name="Hello", category="My category", price=6.7, quantity=5):
    return Product(id=id, name=name, category=category, price=price, quantity=quantity)


def new_user(id="u1", balance=100.2):
    return User(id=id, balance=balance)


def new_auth_record(user_id="u1", username="uname", hashed_password="password"):
    return AuthRecord(
        user_id=user_id, username=username, hashed_password=hashed_password
    )


def new_auth_input(username="uname", password="password"):
    return AuthInput(username=username, password=password)
