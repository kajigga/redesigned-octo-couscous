import { useState, useEffect } from "react";
import { Alert } from "react-bootstrap";
import { useAuth0 } from "@auth0/auth0-react";

export default function AuthErrorAlert() {
  const { error } = useAuth0();
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (error) {
      const desc = error.message || error.error_description || "Authentication error";
      setMessage(desc);
      setVisible(true);
    }
  }, [error]);

  if (!visible) return null;

  return (
    <Alert variant="danger" dismissible onClose={() => setVisible(false)} className="mb-0 rounded-0">
      {message}
    </Alert>
  );
}
