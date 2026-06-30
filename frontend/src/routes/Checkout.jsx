import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Row, Col, Alert } from "react-bootstrap";
import { useAuth0 } from "@auth0/auth0-react";
import { jwtDecode } from "jwt-decode";
import { useCart } from "../context/CartContext";
import { placeOrder } from "../api/orders";

const REQUIRED_SCOPE = "pizza42-order";

export default function Checkout() {
  const { items, subtotal, clearCart } = useCart();
  const { isLoading, user, loginWithRedirect, getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [error, setError] = useState(null);
  const [placing, setPlacing] = useState(false);
  const [accessToken, setAccessToken] = useState(null);
  const [hasScope, setHasScope] = useState(false);

  const address = {
    name: user?.name || user?.nickname || "",
    street: user?.["pizza42/address_street"] || "",
    city: user?.["pizza42/address_city"] || "",
    zip: user?.["pizza42/address_zip"] || "",
  };

  useEffect(() => {
    if (isLoading) return;
    const checkScope = async () => {
      try {
        const token = await getAccessTokenSilently({
          authorizationParams: {
            audience: import.meta.env.VITE_AUTH0_AUDIENCE,
            scope: REQUIRED_SCOPE,
          },
        });
        const decoded = jwtDecode(token);
        if (decoded.scope?.includes(REQUIRED_SCOPE)) {
          setAccessToken(token);
          setHasScope(true);
        } else {
          loginWithRedirect({
            authorizationParams: {
              scope: `openid profile email ${REQUIRED_SCOPE}`,
              audience: import.meta.env.VITE_AUTH0_AUDIENCE,
            },
            appState: { returnTo: "/checkout" },
          });
        }
      } catch (err) {
        console.error("Failed to fetch access token:", err);
      }
    };
    checkScope();
  }, [isLoading, getAccessTokenSilently, loginWithRedirect]);

  if (isLoading || !hasScope) return null;

  if (items.length === 0) {
    return (
      <>
        <h1 className="mb-4">Checkout</h1>
        <Alert variant="info">Your cart is empty. Add some pizzas first!</Alert>
      </>
    );
  }

  const handlePlaceOrder = async () => {
    setPlacing(true);
    setError(null);
    try {
      await placeOrder(
        {
          items: items.map((i) => ({ id: i.id, quantity: i.quantity })),
          total: subtotal,
          address,
        },
        accessToken,
      );
      clearCart();
      navigate("/profile");
    } catch (err) {
      setError(err.message);
      setPlacing(false);
    }
  };

  return (
    <>
      <h1 className="mb-4">Checkout</h1>

      <Row>
        <Col md={7}>
          {step === 1 && (
            <>
              <h4>Review Your Order</h4>
              <Card className="mb-3">
                <Card.Body>
                  <Card.Title>Delivery to</Card.Title>
                  <p className="mb-0">{address.name}</p>
                  <p className="mb-0">{address.street}</p>
                  <p className="mb-0">
                    {address.city}, {address.zip}
                  </p>
                </Card.Body>
              </Card>
              {error && <Alert variant="danger">{error}</Alert>}
              <div className="d-flex gap-2">
                <Button variant="outline-secondary" onClick={() => setStep(1)}>
                  Back
                </Button>
                <Button
                  variant="success"
                  disabled={placing}
                  onClick={handlePlaceOrder}
                >
                  {placing ? "Placing Order..." : "Place Order"}
                </Button>
              </div>
            </>
          )}
        </Col>

        <Col md={5}>
          <Card>
            <Card.Body>
              <Card.Title>Order Summary</Card.Title>
              <ul className="list-unstyled">
                {items.map((item) => (
                  <li
                    key={item.id}
                    className="d-flex justify-content-between mb-1"
                  >
                    <span>
                      {item.quantity}x {item.name}
                    </span>
                    <span>${(item.price * item.quantity).toFixed(2)}</span>
                  </li>
                ))}
              </ul>
              <hr />
              <div className="d-flex justify-content-between fw-bold">
                <span>Total</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </>
  );
}
