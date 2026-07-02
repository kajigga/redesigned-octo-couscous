import logging
import time
from functools import wraps

from sqlalchemy.exc import OperationalError, SQLAlchemyError

from .extensions import db
from .models import MenuItem, Order, OrderItem

logger = logging.getLogger(__name__)


def with_db_retry(max_retries=3, base_delay=1):
    """Decorator that retries database operations on transient connection errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): "
                            f"{str(e)}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        continue
                    logger.error(
                        f"Database operation failed after {max_retries + 1} attempts: {str(e)}"
                    )
                    raise
                except SQLAlchemyError as e:
                    logger.error(f"Database error: {str(e)}")
                    raise
        return wrapper
    return decorator

MENU_SEED = [
    {
        "id": "pepperoni",
        "name": "Pepperoni",
        "description": "Classic pepperoni with mozzarella cheese",
        "price": 12.99,
        "image_url": "https://thumbs.dreamstime.com/b/whole-pepperoni-pizza-1356269.jpg",
    },
    {
        "id": "sausage",
        "name": "Sausage",
        "description": "Italian sausage with mozzarella cheese",
        "price": 13.99,
        "image_url": "https://joyfoodsunshine.com/wp-content/uploads/2023/09/sausage-pizza-recipe-17.jpg",
    },
    {
        "id": "hawaiian",
        "name": "Hawaiian",
        "description": "Ham and pineapple with mozzarella cheese",
        "price": 11.99,
        "image_url": "https://i0.wp.com/dishcrawl.com/wp-content/uploads/2021/08/hawaiian-pizza-recipe.jpg?fit=600%2C600&ssl=1",
    },
]


def init_db():
    """Create all tables and seed the menu."""
    db.create_all()
    for data in MENU_SEED:
        db.session.merge(MenuItem(**data))
    db.session.commit()


@with_db_retry(max_retries=3, base_delay=1)
def insert_order(order_id, user_id, date, total, address, items):
    """Persist a new order with its items to the database."""
    logger.info(f"Inserting order {order_id} for user {user_id}")
    order = Order(
        id=order_id,
        user_id=user_id,
        date=date,
        total=total,
        address_name=address.get("name"),
        street=address.get("street"),
        city=address.get("city"),
        zip=address.get("zip"),
    )
    for item in items:
        order.items.append(
            OrderItem(
                item_id=item["id"],
                name=item["name"],
                quantity=item["quantity"],
                price=item["price"],
            )
        )
    db.session.add(order)
    db.session.commit()
    logger.info(f"Order {order_id} inserted successfully")


@with_db_retry(max_retries=3, base_delay=1)
def fetch_orders_for_user(user_id):
    """Return all orders for a given user, most recent first."""
    logger.info(f"Fetching orders for user {user_id}")
    orders = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.date.desc())
        .all()
    )
    result = []
    for order in orders:
        result.append(
            {
                "id": order.id,
                "date": order.date,
                "items": [
                    {
                        "id": oi.item_id,
                        "name": oi.name,
                        "quantity": oi.quantity,
                        "price": oi.price,
                    }
                    for oi in order.items
                ],
                "total": order.total,
                "status": order.status,
                "address": {
                    "name": order.address_name,
                    "street": order.street,
                    "city": order.city,
                    "zip": order.zip,
                },
            }
        )
    logger.info(f"Fetched {len(result)} orders for user {user_id}")
    return result
