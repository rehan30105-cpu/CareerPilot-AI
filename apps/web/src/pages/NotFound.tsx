import { NavLink } from "react-router-dom";
import { AlertCircle } from "lucide-react";

export function NotFound() {
  return (
    <div className="card text-center py-12">
      <AlertCircle className="w-12 h-12 text-brand-400 mx-auto mb-4" />
      <h2 className="text-brand-900 font-semibold text-xl mb-2">Page not found</h2>
      <p className="text-brand-600 mb-6">
        The page you&rsquo;re looking for doesn&rsquo;t exist yet.
      </p>
      <NavLink to="/" className="btn-primary">
        Return to dashboard
      </NavLink>
    </div>
  );
}
