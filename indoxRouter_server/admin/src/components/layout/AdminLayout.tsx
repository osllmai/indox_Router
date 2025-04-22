
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { cn } from '@/lib/utils';

export const AdminLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="flex h-screen bg-admin-background">
      <Sidebar collapsed={sidebarCollapsed} />
      
      <div className={cn("flex flex-col flex-1 transition-all", 
        sidebarCollapsed ? "ml-20" : "ml-64")}>
        <Navbar onToggleSidebar={toggleSidebar} />
        
        <main className="flex-1 p-6 overflow-auto bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
