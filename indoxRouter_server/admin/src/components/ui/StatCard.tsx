
import React from 'react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  change?: { value: string | number; isPositive: boolean };
  color?: 'blue' | 'green' | 'purple' | 'amber';
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon, 
  change, 
  color = 'blue',
  className 
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
  };

  const iconColorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-emerald-100 text-emerald-600',
    purple: 'bg-purple-100 text-purple-600',
    amber: 'bg-amber-100 text-amber-600',
  };

  return (
    <div className={cn("stat-card p-6 bg-white rounded-xl border shadow-sm", className)}>
      <div className="flex justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-1 text-2xl font-semibold">{value}</p>
          
          {change && (
            <div className="mt-2 flex items-center">
              <span className={cn(
                "text-xs font-medium",
                change.isPositive ? "text-emerald-600" : "text-red-600"
              )}>
                {change.isPositive ? '↑' : '↓'} {change.value}
              </span>
              <span className="ml-1 text-xs text-gray-500">vs. last period</span>
            </div>
          )}
        </div>
        
        <div className={cn(
          "flex items-center justify-center h-12 w-12 rounded-full", 
          iconColorClasses[color]
        )}>
          {icon}
        </div>
      </div>
    </div>
  );
};
