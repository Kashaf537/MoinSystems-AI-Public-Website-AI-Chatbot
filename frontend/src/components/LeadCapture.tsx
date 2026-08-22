interface LeadCaptureProps {
  active: boolean;
}

export default function LeadCapture({
  active,
}: LeadCaptureProps) {

  if (!active) {
    return null;
  }


  return (
    <div
      className="lead-capture-notice"
      role="status"
    >
      <span className="lead-icon">
        ✓
      </span>

      <span>
        Please provide the requested
        contact details to continue.
      </span>
    </div>
  );
}