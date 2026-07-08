import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-solar-600 mb-4">404</h1>
        <p className="text-lg text-gray-500 dark:text-gray-400 mb-6">
          Page not found
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2 bg-solar-600 hover:bg-solar-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Home size={16} />
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
