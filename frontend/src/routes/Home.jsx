import { useState, useEffect } from "react";
import { Row, Col, Spinner, Alert } from "react-bootstrap";
import PizzaCard from "../components/PizzaCard";
import { fetchMenu } from "../api/menu";
import { useCart } from "../context/CartContext";
import fallbackMenu from "../data/menu";

export default function Home() {
  const { addItem } = useCart();
  const [menu, setMenu] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMenu()
      .then(setMenu)
      .catch(() => {
        setMenu(fallbackMenu);
        setError("Could not load live menu — showing cached menu.");
      });
  }, []);

  if (!menu) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <>
      {error && <Alert variant="warning">{error}</Alert>}
      <h1 className="mb-4">Our Menu</h1>
      <Row xs={1} md={3} className="g-4">
        {menu.map((pizza) => (
          <Col key={pizza.id}>
            <PizzaCard pizza={pizza} onAdd={addItem} />
          </Col>
        ))}
      </Row>
    </>
  );
}
