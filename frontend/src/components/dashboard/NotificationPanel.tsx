import { Bell, CheckCircle } from 'lucide-react';

const notifications = [
  { id: 1, text: 'Routine maintenance for SEC01 completed', time: '2 hours ago', read: false },
  { id: 2, text: 'String SEC02-INV01-STR05 back online', time: '5 hours ago', read: false },
  { id: 3, text: 'Weekly report for Week 27 generated', time: '1 day ago', read: true },
  { id: 4, text: 'Firmware update available for 3 inverters', time: '2 days ago', read: true },
];

export function NotificationPanel() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4 flex items-center justify-between">
        <span>Notifications</span>
        <Bell size={16} />
      </h3>
      <div className="space-y-3">
        {notifications.map((n) => (
          <div key={n.id} className="flex items-start gap-3">
            <CheckCircle
              size={16}
              className={`mt-0.5 ${n.read ? 'text-gray-300 dark:text-gray-600' : 'text-solar-600'}`}
            />
            <div>
              <p className={`text-sm ${n.read ? 'text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                {n.text}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">{n.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
