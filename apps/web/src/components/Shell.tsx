import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Settings,
  User,
  Menu,
  X,
  LogOut,
} from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/auth";

interface ShellProps {
  children: React.ReactNode;
}

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resumes", label: "Resumes", icon: FileText },
  { href: "/jobs", label: "Jobs", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Shell({ children }: ShellProps) {
  const { user, logout, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-0 z-30 bg-white border-r border-brand-200 transform transition-transform duration-300 -translate-x-full md:relative md:translate-x-0 md:w-64 md:shadow-sm`}
      >
        <div className="flex items-center justify-between h-12 px-6 border-b border-brand-100">
          <span className="font-bold text-brand-900 text-lg tracking-tight">
            CareerPilot AI
          </span>
          <button
            className="md:hidden p-1 rounded hover:bg-brand-100 text-brand-600"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-accent-50 text-accent-600"
                      : "text-brand-600 hover:bg-brand-100 hover:text-brand-900"
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="mt-auto p-4 border-t border-brand-100">
          <div className="p-2">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 hover:text-red-800 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top bar */}
        <header className="h-12 border-b border-brand-100 bg-white flex items-center justify-between px-6 z-10 md:ml-0">
          <div className="flex items-center gap-4">
            <button
              className="p-1.5 md:hidden rounded hover:bg-brand-100 text-brand-600"
              onClick={() => setSidebarOpen((prev) => !prev)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-brand-900 font-semibold text-lg hidden md:block">
              CareerPilot AI
            </h1>
          </div>
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="hidden md:flex items-center gap-3 px-3 py-1 rounded-lg border border-brand-200 bg-white text-sm">
                <span className="text-brand-600">
                  {user.full_name || user.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="p-1.5 text-brand-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button className="btn-ghost text-brand-600 hover:bg-brand-100">
                <User className="w-5 h-5" />
              </button>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
}

