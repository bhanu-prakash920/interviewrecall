import { Code2 } from "lucide-react";
export function Metric({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof Code2;
  label: string;
  value: number | string;
  detail: string;
}) {
  return (
    <div className="metric glass">
      <div className="metric-label">
        <span>{label}</span>
        <Icon size={17} />
      </div>
      <div className="metric-value">{value}</div>
      <p>{detail}</p>
    </div>
  );
}
