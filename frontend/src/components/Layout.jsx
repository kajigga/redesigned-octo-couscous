import { Navbar, Nav, Container, Badge, Button } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useAuth0 } from "@auth0/auth0-react";
import { useCart } from "../context/CartContext";
import AuthErrorAlert from "./AuthErrorAlert";
import Footer from "./Footer";

export default function Layout({ children }) {
  const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();
  const { itemCount } = useCart();

  const handleLogout = () =>
    logout({ logoutParams: { returnTo: window.location.origin } });

  return (
    <div className="d-flex flex-column min-vh-100">
      <AuthErrorAlert />
      <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
        <Container>
          <LinkContainer to="/">
            <Navbar.Brand>
              <img src="/images/logo_simplified.png" alt="Pizza42" height="32" /> Pizza42
            </Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="main-nav" />
          <Navbar.Collapse id="main-nav">
            <Nav className="me-auto">
              <LinkContainer to="/">
                <Nav.Link>Menu</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/cart">
                <Nav.Link>
                  Cart{" "}
                  {itemCount > 0 && (
                    <Badge bg="danger" pill>
                      {itemCount}
                    </Badge>
                  )}
                </Nav.Link>
              </LinkContainer>
              {isAuthenticated && (
                <LinkContainer to="/profile">
                  <Nav.Link>Profile</Nav.Link>
                </LinkContainer>
              )}
            </Nav>
            <Nav>
              {isAuthenticated ? (
                <>
                  <Navbar.Text className="me-2">
                    {user.email}
                  </Navbar.Text>
                  <Button variant="outline-light" size="sm" onClick={handleLogout}>
                    Logout
                  </Button>
                </>
              ) : (
                <Button variant="outline-light" size="sm" onClick={() => loginWithRedirect()}>
                  Login
                </Button>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container className="py-4 flex-grow-1">{children}</Container>
      <Footer />
    </div>
  );
}
