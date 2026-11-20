import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Mail, Lock, User as UserIcon, AlertCircle, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import type { RegisterData } from "@/types/auth";

export function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState<RegisterData>({
    email: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await api.post("/api/v1/auth/register", {
        email: form.email,
        password: form.password,
        full_name: form.full_name || undefined,
      });

      navigate("/login", {
        state: { registered: true, email: form.email },
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Registration failed. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-brand-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-brand-900 tracking-tight">
            Create account
          </h1>
          <p className="mt-2 text-brand-600">
            Start managing your career with AI
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
              htmlFor="full_name"
              className="block text-sm font-medium text-brand-700 mb-1"
            >
              Full name
            </label>
            <div className="relative">
              <UserIcon
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-400"
              />
              <input
                id="full_name"
                type="text"
                autoComplete="name"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-brand-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-accent-600 focus:border-transparent disabled:opacity-50 disabled:pointer-events-none"
                placeholder="Jane Doe"
              />
            </div>
          </div>

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
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
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
                autoComplete="new-password"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-brand-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-accent-600 focus:border-transparent disabled:opacity-50 disabled:pointer-events-none"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-brand-400">
                8+ chars
              </span>
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
                Creating account…
              </>
            ) : (
              <>
                <ArrowRight className="w-4 h-4" />
                Create account
              </>
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-brand-600">
          Already have an account?{" "}
          <NavLink to="/login" className="text-accent-600 font-medium hover:underline">
            Sign in
          </NavLink>
        </p>
      </div>
    </div>
  );
}
