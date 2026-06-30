import { Row, Col } from "react-bootstrap";
import menu from "../data/menu";
import PizzaCard from "../components/PizzaCard";
import { useCart } from "../context/CartContext";

export default function Home() {
  const { addItem } = useCart();

  return (
    <>
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
