import { Row, Col, Button } from "react-bootstrap";

export default function CartItem({ item, onUpdateQty, onRemove }) {
  return (
    <Row className="align-items-center border-bottom py-2">
      <Col xs={4}>
        <strong>{item.name}</strong>
      </Col>
      <Col xs={2} className="text-center">
        ${item.price.toFixed(2)}
      </Col>
      <Col xs={3} className="d-flex align-items-center gap-2">
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => onUpdateQty(item.id, item.quantity - 1)}
        >
          -
        </Button>
        <span>{item.quantity}</span>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => onUpdateQty(item.id, item.quantity + 1)}
        >
          +
        </Button>
      </Col>
      <Col xs={2} className="text-end">
        ${(item.price * item.quantity).toFixed(2)}
      </Col>
      <Col xs={1} className="text-end">
        <Button
          variant="outline-danger"
          size="sm"
          onClick={() => onRemove(item.id)}
        >
          &times;
        </Button>
      </Col>
    </Row>
  );
}
