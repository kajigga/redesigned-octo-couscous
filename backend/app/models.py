from .extensions import db


class MenuItem(db.Model):
    __tablename__ = "menu"

    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="received")
    address_name = db.Column(db.String(255))
    street = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip = db.Column(db.String(20))

    items = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("idx_orders_user", "user_id"),)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_id = db.Column(
        db.String(255), db.ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    item_id = db.Column(
        db.String(255), db.ForeignKey("menu.id"), primary_key=True
    )
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship("Order", back_populates="items")
