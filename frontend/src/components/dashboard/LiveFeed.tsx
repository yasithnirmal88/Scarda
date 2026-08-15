import { Activity, Radio, Zap, CloudSun, AlertTriangle } from 'lucide-react';
import { useLiveData } from '../../hooks/useLiveData';

/**
 * Live data feed — shows the 10-minute readings/weather/alerts the backend
 * pushes over WebSocket. All values originate from the data provider; the
 * frontend never fabricates them.
 */
export function LiveFeed() {
  const { status, lastReading, lastWeather, alerts, lastUpdated } = useLiveData();

  const statusColor =
    status === 'open'
      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
      : status === 'connecting'
        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <Activity size={16} /> Live Feed (10-min)
        </h3>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor} flex items-center gap-1`}>
          <Radio size={12} />
          {status === 'open' ? 'Live' : status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-900/20">
            <Zap size={18} className="text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Live Power</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {lastReading?.power_w != null
                ? `${(lastReading.power_w / 1000).toFixed(2)} kW`
                : '—'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-900/20">
            <CloudSun size={18} className="text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Irradiance</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {lastWeather?.irradiance_wpm2 != null
                ? `${Math.round(lastWeather.irradiance_wpm2)} W/m²`
                : '—'}
            </p>
          </div>
        </div>
      </div>

      {alerts.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1">
            <AlertTriangle size={12} /> Live Alerts
          </p>
          {alerts.slice(0, 3).map((a) => (
            <div
              key={a.alert_id}
              className="text-xs p-2 rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300"
            >
              <span className="font-medium">{a.alert_type}</span> on {a.string_id}
              {a.deviation_pct != null && ` (deviation ${a.deviation_pct.toFixed(1)}%)`}
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 dark:text-gray-500 mt-3">
        {lastUpdated
          ? `Updated ${lastUpdated.toLocaleTimeString()}`
          : 'Waiting for data…'}
      </p>
    </div>
  );
}
