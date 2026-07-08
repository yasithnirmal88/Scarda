import { createBrowserRouter, Navigate } from 'react-router-dom';

import { AuthLayout } from '../layouts/AuthLayout';
import { MainLayout } from '../layouts/MainLayout';
import { Alerts } from '../pages/Alerts';
import { Dashboard } from '../pages/Dashboard';
import { Inverters } from '../pages/Inverters';
import { Login } from '../pages/Login';
import { NotFound } from '../pages/NotFound';
import { Reports } from '../pages/Reports';
import { Sections } from '../pages/Sections';
import { Settings } from '../pages/Settings';
import { Strings } from '../pages/Strings';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <Login /> },
    ],
  },
  {
    element: <MainLayout />,
    children: [
      { path: '/dashboard', element: <Dashboard /> },
      { path: '/sections', element: <Sections /> },
      { path: '/inverters', element: <Inverters /> },
      { path: '/strings', element: <Strings /> },
      { path: '/alerts', element: <Alerts /> },
      { path: '/reports', element: <Reports /> },
      { path: '/settings', element: <Settings /> },
    ],
  },
  { path: '*', element: <NotFound /> },
]);
