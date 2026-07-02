import { Container } from "react-bootstrap";

export default function Footer() {
  const version = import.meta.env.VITE_APP_VERSION;
  return (
    <footer className="bg-dark text-white py-3 mt-auto">
      <Container className="d-flex align-items-center justify-content-between">
        <img src="/images/logo_simplified.png" alt="Pizza42" height="20" />

        <span className="small">
          Copyright {new Date().getFullYear()} | Bongawonga | {version && <>v{version} &middot; </>}
        </span>
      </Container>
    </footer>
  );
}
