import { Circle, AlertCircle, Database, ShieldCheck } from "lucide-react";
import type { HealthStatus, DatabaseHealthStatus } from "@/types";

type StatusVariant = "ok" | "degraded" | "error" | "unknown";

function statusColor(status: StatusVariant) {
  switch (status) {
    case "ok":
      return "text-green-600 border-green-200 bg-green-50";
    case "degraded":
      return "text-amber-600 border-amber-200 bg-amber-50";
    case "error":
      return "text-red-600 border-red-200 bg-red-50";
    default:
      return "text-brand-500 border-brand-200 bg-brand-50";
  }
}

function statusIcon(status: StatusVariant) {
  switch (status) {
    case "ok":
      return <Circle className="w-4 h-4 fill-green-600" />;
    case "degraded":
      return <AlertCircle className="w-4 h-4 fill-amber-600" />;

    case "error":
      return <AlertCircle className="w-4 h-4 fill-red-600" />;
    default:
      return <ShieldCheck className="w-4 h-4 fill-brand-500" />;
  }
}

interface HealthIndicatorProps {
  label: string;
  health: HealthStatus | DatabaseHealthStatus | null;
}

export function HealthIndicator({
  label,
  health,
}: HealthIndicatorProps) {
  if (!health) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-brand-200 bg-brand-50 text-brand-600 text-sm">
        <ShieldCheck className="w-4 h-4 fill-brand-500" />
        <span>{label}</span>
        <span className="ml-auto">—</span>
      </div>
    );
  }

  const status: StatusVariant =
    health.status === "ok" ? "ok" : health.status === "degraded" ? "degraded" : "error";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border">
      <span className={`flex items-center gap-1 ${statusColor(status)}`}>
        {statusIcon(status)}
        <span>{health.status}</span>
      </span>
      <span className="text-xs text-brand-600">{label}</span>
    </div>
  );
}

export function DatabaseHealthIndicator({
  health,
}: {
  health: DatabaseHealthStatus | null;
}) {
  if (!health) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-brand-200 bg-brand-50 text-brand-600 text-sm">
        <Database className="w-4 h-4 fill-brand-500" />
        <span>Database</span>
        <span className="ml-auto">—</span>
      </div>
    );
  }

  const status: StatusVariant =
    health.status === "ok" ? "ok" : health.status === "degraded" ? "degraded" : "error";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border">
      <span className={`flex items-center gap-1 ${statusColor(status)}`}>
        {statusIcon(status)}
        <span>{health.status}</span>
      </span>
      <span className="text-xs text-brand-600">Database</span>
      {health.detail && (
        <span className="text-xs text-brand-500 ml-2">({health.detail})</span>
      )}
    </div>
  );
}
