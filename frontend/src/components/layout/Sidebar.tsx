import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Table2,
  Zap,
  Cable,
  Bell,
  FileText,
  Wrench,
  Settings,
  LogOut,
  X,
} from 'lucide-react';
import { classNames } from '../../utils/helpers';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  onClose: () => void;
}

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Sections', path: '/sections', icon: Table2 },
  { label: 'Inverters', path: '/inverters', icon: Zap },
  { label: 'Strings', path: '/strings', icon: Cable },
  { label: 'Alerts', path: '/alerts', icon: Bell },
  { label: 'Reports', path: '/reports', icon: FileText },
  { label: 'Maintenance', path: '/maintenance', icon: Wrench },
  { label: 'Settings', path: '/settings', icon: Settings },
];

export function Sidebar({ collapsed, onToggle, onClose }: SidebarProps) {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    classNames(
      'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
      isActive
        ? 'bg-solar-600 text-white'
        : 'text-gray-300 hover:bg-gray-700 hover:text-white',
    );

  return (
    <>
      {!collapsed && (
        <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={classNames(
          'fixed lg:static inset-y-0 left-0 z-30 flex flex-col bg-gray-900 transition-all duration-300',
          collapsed ? 'w-0 -translate-x-full lg:w-16 lg:translate-x-0' : 'w-64',
        )}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-700">
          {!collapsed && (
            <span className="text-lg font-bold text-white">Solar AIM</span>
          )}
          <button
            onClick={collapsed ? onToggle : onClose}
            className="lg:hidden p-1 text-gray-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={linkClass}
              title={collapsed ? item.label : undefined}
            >
              <item.icon size={20} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-700">
          <button
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
          >
            <LogOut size={20} />
            {!collapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
