from app.models.order import Order


def new_order(id="o1", user_id="u1", product_ids: tuple[str, ...] = ("p1", "p2")):
    Order(id="o1", user_id="u1", product_ids=product_ids)
    return Order(id, user_id, product_ids)
