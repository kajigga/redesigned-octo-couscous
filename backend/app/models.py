from .extensions import db


class MenuItem(db.Model):
    __tablename__ = "menu"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default="received")
    address_name = db.Column(db.String)
    street = db.Column(db.String)
    city = db.Column(db.String)
    zip = db.Column(db.String)

    items = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("idx_orders_user", "user_id"),)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_id = db.Column(
        db.String, db.ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    item_id = db.Column(
        db.String, db.ForeignKey("menu.id"), primary_key=True
    )
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship("Order", back_populates="items")
