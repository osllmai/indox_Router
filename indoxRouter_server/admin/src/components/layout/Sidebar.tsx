import React from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  Users,
  LayoutDashboard,
  Key,
  Settings,
  LogOut,
  Database,
  Terminal,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  collapsed: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const location = useLocation();
  const { logout, user } = useAuth();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Users", path: "/users", icon: Users },
    { name: "API Keys", path: "/api-keys", icon: Key },
    { name: "Transactions", path: "/transactions", icon: Database },
    { name: "Endpoint Tester", path: "/endpoint-tester", icon: Terminal },
    { name: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 bg-admin-primary text-white transition-all duration-300 flex flex-col",
        collapsed ? "w-20" : "w-64"
      )}
    >
      <div className="flex items-center justify-center p-6 border-b border-gray-800">
        {collapsed ? (
          <span className="text-2xl font-bold text-admin-secondary">IR</span>
        ) : (
          <span className="text-xl font-bold">Indox Router</span>
        )}
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center px-4 py-3 rounded-md transition-colors",
              location.pathname === item.path
                ? "bg-slate-800 text-admin-secondary"
                : "text-gray-300 hover:bg-slate-800 hover:text-white",
              collapsed && "justify-center px-0"
            )}
          >
            <item.icon size={20} className={cn(collapsed ? "mx-0" : "mr-3")} />
            {!collapsed && <span>{item.name}</span>}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center mb-4">
          {!collapsed && user && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user.name}
              </p>
              <p className="text-xs text-gray-400">Admin</p>
            </div>
          )}
          <button
            onClick={logout}
            className={cn(
              "flex items-center text-gray-300 hover:text-white",
              collapsed ? "justify-center w-full" : "px-2 py-1"
            )}
          >
            <LogOut size={20} />
            {!collapsed && <span className="ml-2">Logout</span>}
          </button>
        </div>
      </div>
    </aside>
  );
};
