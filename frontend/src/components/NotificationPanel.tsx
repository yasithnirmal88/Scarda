export function NotificationPanel() {
  const notifications = [
    { id: 1, message: 'Inverter INV-05 went offline', time: '2m ago', type: 'error' },
    { id: 2, message: 'String STR-12 power below threshold', time: '15m ago', type: 'warning' },
    { id: 3, message: 'Daily energy target exceeded', time: '1h ago', type: 'success' },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold mb-2">Notifications</h3>
      <ul className="space-y-2">
        {notifications.map((n) => (
          <li key={n.id} className="text-sm flex justify-between">
            <span>{n.message}</span>
            <span className="text-gray-400 text-xs">{n.time}</span>
          </li>
        ))}
      </ul>
      <p className="text-xs text-gray-400 mt-2">Placeholder notifications</p>
    </div>
  );
}
