import { Outlet } from 'react-router-dom';
import { Sun } from 'lucide-react';

export function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-solar-50 via-white to-solar-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-solar-600 mb-4">
            <Sun size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Solar AIM</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Solar Power Plant Monitoring
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
