import { Outlet } from 'react-router-dom';

import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';

export function MainLayout() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
