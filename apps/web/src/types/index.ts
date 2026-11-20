export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface DatabaseHealthStatus {
  status: string;
  database: string;
  detail?: string | null;
}

export interface ApiHealthResponse {
  api: HealthStatus;
  database: DatabaseHealthStatus;
}
