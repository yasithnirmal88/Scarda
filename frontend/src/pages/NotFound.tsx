import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div className="text-center space-y-4">
      <h1 className="text-6xl font-bold text-gray-300">404</h1>
      <p className="text-gray-500">Page not found</p>
      <Link to="/dashboard" className="text-blue-600 underline">
        Go to Dashboard
      </Link>
    </div>
  );
}
