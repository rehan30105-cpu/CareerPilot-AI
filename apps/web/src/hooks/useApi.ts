import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { HealthStatus, DatabaseHealthStatus } from "@/types";

export function useApi() {
  const [apiHealth, setApiHealth] = useState<HealthStatus | null>(null);
  const [dbHealth, setDbHealth] = useState<DatabaseHealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [apiRes, dbRes] = await Promise.allSettled([
        api.get<HealthStatus>("/api/v1/health"),
        api.get<DatabaseHealthStatus>("/api/v1/health/db"),
      ]);

      if (apiRes.status === "fulfilled") {
        setApiHealth(apiRes.value);
      } else {
        setApiHealth(null);
      }

      if (dbRes.status === "fulfilled") {
        setDbHealth(dbRes.value);
      } else {
        setDbHealth({
          status: "degraded",
          database: "postgresql",
          detail: "unable to connect",
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return { apiHealth, dbHealth, loading, error, refetch: fetchHealth };
}
