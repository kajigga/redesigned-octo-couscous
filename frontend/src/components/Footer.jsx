import { Container } from "react-bootstrap";

export default function Footer() {
  const sha = import.meta.env.VITE_GIT_SHA;
  return (
    <footer className="bg-dark text-white py-3 mt-auto">
      <Container className="d-flex align-items-center justify-content-between">
        <img src="/images/pizza42_logo.png" alt="Pizza42" height="20" />
        <span className="small">
          Copyright {new Date().getFullYear()} | Bongawonga | {sha && <>{sha} &middot; </>}
        </span>
      </Container>
    </footer>
  );
}
