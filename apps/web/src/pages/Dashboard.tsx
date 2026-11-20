import { useApi } from "@/hooks/useApi";
import {
  HealthIndicator,
  DatabaseHealthIndicator,
} from "@/components/HealthIndicator";
import { ArrowRight, Clock } from "lucide-react";

export function Dashboard() {
  const { apiHealth, dbHealth, loading, error, refetch } = useApi();

  return (
    <div className="space-y-6">
      <div>
        <h1>Dashboard</h1>
        <p className="text-brand-600">
          Foundation health check — verify backend connectivity before building
          features.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-brand-900 font-semibold">API Status</h3>
              <p className="text-brand-500 text-sm">
                FastAPI backend connectivity
              </p>
            </div>
            <HealthIndicator label="API" health={apiHealth} />
          </div>
          {apiHealth && (
            <div className="mt-4 text-sm text-brand-500">
              {apiHealth.service} v{apiHealth.version} • {apiHealth.environment}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-brand-900 font-semibold">Database Status</h3>
              <p className="text-brand-500 text-sm">
                PostgreSQL connectivity
              </p>
            </div>
            <DatabaseHealthIndicator health={dbHealth} />
          </div>
          {dbHealth && dbHealth.detail && (
            <div className="mt-4 text-sm text-brand-500">
              {dbHealth.detail}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-brand-900 font-semibold">Frontend</h3>
              <p className="text-brand-500 text-sm">
                React + Vite development server
              </p>
            </div>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-green-100 text-green-700 text-xs font-medium border border-green-200">
              <ArrowRight className="w-3 h-3" />
              Running
            </span>
          </div>
          <div className="mt-4 text-sm text-brand-500">
            Port 5173 • proxying /api to :8000
          </div>
        </div>
      </div>

      {loading && (
        <div className="card text-center py-8">
          <Clock className="w-6 h-6 mx-auto text-brand-400 animate-spin mb-2" />
          <p className="text-brand-500">Checking backend health…</p>
        </div>
      )}

      {error && (
        <div className="card border-red-200 bg-red-50 p-4">
          <h3 className="text-red-800 font-semibold">Unable to reach backend</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button
            onClick={refetch}
            className="mt-3 btn-outline text-red-600 hover:bg-red-100"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && apiHealth && dbHealth && (
        <div className="card">
          <h3 className="text-brand-900 font-semibold mb-3">Next steps</h3>
          <ul className="list-disc list-inside text-brand-600 text-sm space-y-2">
            <li>
              Start the backend: <code className="bg-brand-100 px-1.5 py-0.5 rounded text-sm">uvicorn app.main:app --reload</code>
            </li>
            <li>
              Verify <code>/api/v1/health</code> returns <code>200 OK</code>
            </li>
            <li>
              Configure <code>.env</code> with your database credentials
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
