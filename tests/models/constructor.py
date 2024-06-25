from app.models.order import Order, OrderItem, PurchaseInfo
from app.models.product import Product
from app.models.user import User


def new_order(
    id="o1",
    user_id="u1",
    purchase_info=PurchaseInfo(
        (OrderItem(product_id="p1", quantity=2), OrderItem(product_id="p2", quantity=3))
    ),
):
    return Order(id=id, user_id=user_id, purchase_info=purchase_info)


def new_product(id="p1", name="Hello", category="My category", price=6.7, quantity=5):
    return Product(id=id, name=name, category=category, price=price, quantity=quantity)


def new_user(id="u1", balance=100.2):
    return User(id=id, balance=balance)
