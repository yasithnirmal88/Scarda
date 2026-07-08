import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthLayout } from './components/layout/AuthLayout';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/routing/ProtectedRoute';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Sections } from './pages/Sections';
import { Inverters } from './pages/Inverters';
import { StringsPage } from './pages/Strings';
import { AlertsPage } from './pages/Alerts';
import { Reports } from './pages/Reports';
import { Maintenance } from './pages/Maintenance';
import { Settings } from './pages/Settings';
import { NotFound } from './pages/NotFound';

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
      </Route>

      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sections" element={<Sections />} />
        <Route path="/inverters" element={<Inverters />} />
        <Route path="/strings" element={<StringsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/maintenance" element={<Maintenance />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
