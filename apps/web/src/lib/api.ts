/**
 * API client for CareerPilot AI frontend.
 *
 * All requests go through this wrapper so we can centralise:
 * - base URL (from VITE_API_URL, proxied to /api in dev)
 * - error handling
 * - typed responses
 * - automatic auth header injection
 */

const BASE_URL = (import.meta as { env?: { VITE_API_URL?: string } }).env
  ?.VITE_API_URL || "/api";

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      headers: {
        ...headers,
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(
        errorBody.message || `Request failed with status ${response.status}`,
      );
    }

    return response.json() as Promise<T>;
  }

  get<T>(path: string, headers?: Record<string, string>) {
    return this.request<T>(path, { method: "GET", headers });
  }

  post<T>(path: string, body?: unknown, headers?: Record<string, string>) {
    return this.request<T>(path, {
      method: "POST",
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  }
}

export const api = new ApiClient(BASE_URL);
