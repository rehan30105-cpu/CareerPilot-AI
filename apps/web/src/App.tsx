import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Shell } from "@/components/Shell";
import { Dashboard } from "@/pages/Dashboard";
import { NotFound } from "@/pages/NotFound";

function RouteShell({ children }: { children?: React.ReactNode }) {
  return <Shell>{children}</Shell>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RouteShell />}>
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
