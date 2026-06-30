import { Card, Badge } from "react-bootstrap";

function statusVariant(status) {
  switch (status) {
    case "delivered":
      return "success";
    case "preparing":
      return "warning";
    case "cancelled":
      return "danger";
    default:
      return "secondary";
  }
}

export default function OrderCard({ order }) {
  const date = new Date(order.date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <Card className="mb-3">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <Card.Title>Order #{order.id}</Card.Title>
            <Card.Subtitle className="mb-2 text-muted">{date}</Card.Subtitle>
          </div>
          <Badge bg={statusVariant(order.status)}>{order.status}</Badge>
        </div>
        <ul className="list-unstyled mb-2">
          {order.items.map((item) => (
            <li key={item.id}>
              {item.quantity}x {item.name} — ${(item.price * item.quantity).toFixed(2)}
            </li>
          ))}
        </ul>
        <div className="d-flex justify-content-between">
          <small className="text-muted">
            Delivered to {order.address.street}, {order.address.city}
          </small>
          <strong>Total: ${order.total.toFixed(2)}</strong>
        </div>
      </Card.Body>
    </Card>
  );
}
