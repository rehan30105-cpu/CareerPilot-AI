import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Shell } from "@/components/Shell";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Dashboard } from "@/pages/Dashboard";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";
import { NotFound } from "@/pages/NotFound";
import { useAuthStore } from "@/store/auth";
import { useEffect } from "react";

function RouteShell({ children }: { children?: React.ReactNode }) {
  return <Shell>{children}</Shell>;
}

export default function App() {
  const { isAuthenticated, isLoading, clearAuth } = useAuthStore();

  // Clear auth on page load if token is missing from storage
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      clearAuth();
    }
  }, [isAuthenticated, isLoading, clearAuth]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          element={
            <>
              <ProtectedRoute>
                <RouteShell />
              </ProtectedRoute>
            </>
          }>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Navigate to="/" replace />} />
          <Route path="resumes" element={<div className="card">Resumes page — coming in M2</div>} />
          <Route path="jobs" element={<div className="card">Jobs page — coming in M3</div>} />
          <Route path="settings" element={<div className="card">Settings page — coming in M1</div>} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
