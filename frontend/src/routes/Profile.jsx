import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { jwtDecode } from "jwt-decode";
import { Alert, Card } from "react-bootstrap";
import OrderCard from "../components/OrderCard";
import VerifiedBadge from "../components/VerifiedBadge";
import mockOrders from "../mocks/orders";

function decodeJwtPayload(token) {
  try {
    return jwtDecode(token);
  } catch {
    return null;
  }
}

export default function Profile() {
  const { user, getAccessTokenSilently } = useAuth0();
  const [tokens, setTokens] = useState(null);

  const orders = user?.["pizza42/orders"] || mockOrders;

  console.log('user', user);

  useEffect(() => {
    const fetchTokens = async () => {
      try {
        const response = await getAccessTokenSilently({ detailedResponse: true });
        setTokens(response);
      } catch (err) {
        console.error("Failed to fetch tokens:", err);
      }
    };
    fetchTokens();
  }, [getAccessTokenSilently]);

  return (
    <>
      <h1 className="mb-2">My Orders</h1>
      <p className="text-muted mb-4">
        {user?.email}
        {user?.email_verified && <VerifiedBadge label="Email verified" />}
      </p>

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Delivery Address</Card.Title>
          <p className="mb-0">{user?.name || user?.nickname}</p>
          <p className="mb-0">{user?.["pizza42/address_street"]}</p>
          <p className="mb-0">
            {user?.["pizza42/address_city"]}, {user?.["pizza42/address_zip"]}
          </p>
        </Card.Body>
      </Card>

      {orders.length === 0 ? (
        <Alert variant="info">You haven't placed any orders yet.</Alert>
      ) : (
        orders.map((order) => <OrderCard key={order.id} order={order} />)
      )}

      {tokens?.access_token && (
        <Card className="mb-3">
          <Card.Body>
            <Card.Title>Access Token</Card.Title>
            <pre
              className="bg-light p-3 rounded mb-0"
              style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}
            >
              <code>{tokens.access_token}</code>
            </pre>
            <Card.Title className="mt-3">Decoded Payload</Card.Title>
            <pre
              className="bg-light p-3 rounded mb-0"
              style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}
            >
              <code>
                {JSON.stringify(decodeJwtPayload(tokens.access_token), null, 2)}
              </code>
            </pre>
          </Card.Body>
        </Card>
      )}

      {tokens?.id_token && (
        <Card className="mb-3">
          <Card.Body>
            <Card.Title>ID Token</Card.Title>
            <pre
              className="bg-light p-3 rounded mb-0"
              style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}
            >
              <code>{tokens.id_token}</code>
            </pre>
            <Card.Title className="mt-3">Decoded Payload</Card.Title>
            <pre
              className="bg-light p-3 rounded mb-0"
              style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}
            >
              <code>
                {JSON.stringify(decodeJwtPayload(tokens.id_token), null, 2)}
              </code>
            </pre>
          </Card.Body>
        </Card>
      )}
    </>
  );
}
