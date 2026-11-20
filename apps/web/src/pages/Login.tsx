import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Mail, Lock, AlertCircle, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import type { UserRead } from "@/types/auth";

export function Login() {
  const navigate = useNavigate();
  const { login, setLoading } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    setLoading(true);

    try {
      const tokenResponse = await api.post<{
        access_token: string;
        refresh_token: string;
        token_type: string;
      }>("/api/v1/auth/login", { email, password });

      // Fetch the user profile after obtaining the access token
      const user = await api.get<UserRead>("/api/v1/auth/me");

      login(tokenResponse.access_token, user);
      navigate("/");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-brand-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-brand-900 tracking-tight">
            Sign in
          </h1>
          <p className="mt-2 text-brand-600">
            Welcome back to CareerPilot AI
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-md border border-red-200 bg-red-50 text-red-800 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-brand-700 mb-1"
            >
              Email address
            </label>
            <div className="relative">
              <Mail
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-400"
              />
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-brand-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-accent-600 focus:border-transparent disabled:opacity-50 disabled:pointer-events-none"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-brand-700 mb-1"
            >
              Password
            </label>
            <div className="relative">
              <Lock
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-400"
              />
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-brand-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-accent-600 focus:border-transparent disabled:opacity-50 disabled:pointer-events-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg bg-accent-600 text-white border border-transparent hover:bg-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-600 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none transition-colors"
          >
            {isSubmitting ? (
              <>
                <ArrowRight className="w-4 h-4 animate-spin" />
                Signing in…
              </>
            ) : (
              <>
                <ArrowRight className="w-4 h-4" />
                Sign in
              </>
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-brand-600">
          Don't have an account?{" "}
          <NavLink to="/register" className="text-accent-600 font-medium hover:underline">
            Create an account
          </NavLink>
        </p>
      </div>
    </div>
  );
}
