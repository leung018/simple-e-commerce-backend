from app.models.order import Order
from app.models.product import Product
from app.models.user import User


def new_order(
    id="o1", user_id="u1", product_ids: frozenset[str] = frozenset(["p1", "p2"])
):
    Order(id="o1", user_id="u1", product_ids=product_ids)
    return Order(id, user_id, product_ids)


def new_product(id="p1", name="Hello", category="My category", price=6.7, quantity=5):
    return Product(id=id, name=name, category=category, price=price, quantity=quantity)


def new_user(id="u1", balance=100.2):
    return User(id=id, balance=balance)
