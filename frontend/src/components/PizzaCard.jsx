import { Card, Button } from "react-bootstrap";

export default function PizzaCard({ pizza, onAdd }) {
  return (
    <Card>
      {pizza.imageUrl && (
        <Card.Img variant="top" src={pizza.imageUrl} 
          style={{ height: "200px", objectFit: "cover" }}
		  alt={pizza.name} />
      )}
      <Card.Body>
        <Card.Title>{pizza.name}</Card.Title>
        <Card.Text>{pizza.description}</Card.Text>
        <Card.Text className="fs-4 fw-bold text-primary">
          ${pizza.price.toFixed(2)}
        </Card.Text>
        <Button variant="primary" onClick={() => onAdd(pizza)}>
          Add to Cart
        </Button>
      </Card.Body>
    </Card>
  );
}
