import type { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: ReactNode;
  trend?: { value: number; isUp: boolean };
}

export function StatCard({ title, value, subtitle, icon, trend }: StatCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <p className={`text-xs mt-2 flex items-center gap-1 ${trend.isUp ? 'text-green-600' : 'text-red-600'}`}>
              <span>{trend.isUp ? '↑' : '↓'}</span>
              {trend.value}% vs yesterday
            </p>
          )}
        </div>
        {icon && (
          <div className="p-2 rounded-lg bg-solar-50 dark:bg-solar-900/30 text-solar-600 dark:text-solar-400">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
