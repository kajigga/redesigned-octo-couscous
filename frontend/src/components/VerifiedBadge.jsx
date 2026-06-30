export default function VerifiedBadge({ size = 16, label = "Verified" }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      fill="currentColor"
      className="bi bi-check-circle-fill text-success ms-2"
      viewBox="0 0 16 16"
      role="img"
      aria-label={label}
    >
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM6.97 9.425l-.97-.97a.75.75 0 0 0-1.06 1.06l1.5 1.5a.75.75 0 0 0 1.06 0l3.5-3.5a.75.75 0 0 0-1.06-1.06l-2.97 2.97z" />
    </svg>
  );
}
