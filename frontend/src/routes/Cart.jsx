import { useNavigate } from "react-router-dom";
import { Button, Alert } from "react-bootstrap";
import { useAuth0 } from "@auth0/auth0-react";
import { useCart } from "../context/CartContext";
import CartItem from "../components/CartItem";

const REQUIRED_SCOPE = "pizza42-order";

export default function Cart() {
  const { items, updateQty, removeItem, subtotal, clearCart } = useCart();
  const { isAuthenticated, user, loginWithRedirect } = useAuth0();
  const navigate = useNavigate();

  const handleCheckout = () => {
    const hasScope = user?.scope?.includes(REQUIRED_SCOPE);

    if (isAuthenticated && hasScope) {
      navigate("/checkout");
      return;
    }

    loginWithRedirect({
      appState: { returnTo: "/checkout" },
      authorizationParams: {
        scope: `openid profile email ${REQUIRED_SCOPE}`,
      },
    });
  };

  if (items.length === 0) {
    return (
      <>
        <h1 className="mb-4">Your Cart</h1>
        <Alert variant="info">Your cart is empty.</Alert>
      </>
    );
  }

  return (
    <>
      <h1 className="mb-4">Your Cart</h1>
      <div className="border-top">
        <div className="border-bottom py-2 fw-bold">
          <div className="row">
            <div className="col-4">Item</div>
            <div className="col-2 text-center">Price</div>
            <div className="col-3 text-center">Quantity</div>
            <div className="col-2 text-end">Subtotal</div>
            <div className="col-1" />
          </div>
        </div>
        {items.map((item) => (
          <CartItem
            key={item.id}
            item={item}
            onUpdateQty={updateQty}
            onRemove={removeItem}
          />
        ))}
      </div>
      <div className="d-flex justify-content-between align-items-center mt-3">
        <Button variant="outline-danger" onClick={clearCart}>
          Clear Cart
        </Button>
        <h4 className="mb-0">Total: ${subtotal.toFixed(2)}</h4>
      </div>
      <div className="d-flex justify-content-end mt-3">
        <Button variant="primary" size="lg" onClick={handleCheckout}>
          {isAuthenticated ? "Proceed to Checkout" : "Login to Checkout"}
        </Button>
      </div>
    </>
  );
}
