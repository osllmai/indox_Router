
import React from 'react';
import { Menu, Bell, Search } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface NavbarProps {
  onToggleSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { user } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between h-16 px-6">
        <div className="flex items-center">
          <button 
            onClick={onToggleSidebar}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
          >
            <Menu size={20} />
          </button>
          
          <div className="ml-6 relative w-64">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <Search size={16} className="text-gray-400" />
            </div>
            <input 
              type="text" 
              placeholder="Search..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-admin-accent focus:border-admin-accent text-sm"
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100 focus:outline-none">
            <Bell size={20} />
          </button>
          
          <div className="flex items-center">
            {user && (
              <>
                <img 
                  src={user.avatar} 
                  alt="User avatar" 
                  className="h-8 w-8 rounded-full object-cover border border-gray-200"
                />
                <span className="ml-2 text-sm font-medium">{user.name}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
