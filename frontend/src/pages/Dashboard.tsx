import { useQuery } from '@tanstack/react-query';
import { PlantOverview } from '../components/dashboard/PlantOverview';
import { WeatherWidget } from '../components/dashboard/WeatherWidget';
import { RecentAlerts } from '../components/dashboard/RecentAlerts';
import { SystemStatusCard } from '../components/dashboard/SystemStatusCard';
import { NotificationPanel } from '../components/dashboard/NotificationPanel';
import { PowerChart } from '../components/charts/PowerChart';
import { PlantHeatmap } from '../components/heatmap/PlantHeatmap';
import { dashboardService, type DashboardResponse } from '../services/dashboardService';
import { readingService } from '../services/readingService';
import type { ChartDataPoint } from '../types';
import { useState, useEffect } from 'react';

const REFRESH_INTERVAL = 30_000;

export function Dashboard() {
  // Chart data is seeded only from real backend responses; no mock data.
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  const dashQuery = useQuery<DashboardResponse>({
    queryKey: ['dashboard'],
    queryFn: dashboardService.get,
    refetchInterval: REFRESH_INTERVAL,
    retry: 2,
    staleTime: 10_000,
  });

  const historyQuery = useQuery({
    queryKey: ['reading-history'],
    queryFn: () => readingService.getHistory(24),
    refetchInterval: REFRESH_INTERVAL,
    retry: 1,
    staleTime: 30_000,
    enabled: false,
  });

  useEffect(() => {
    if (dashQuery.data) {
      const d = dashQuery.data;
      const point: ChartDataPoint = {
        time: new Date(d.timestamp).toLocaleTimeString(),
        power: d.power.total_power_kw,
        voltage: d.weather.irradiance_wpm2 ?? 0,
        current: d.power.total_power_kw,
        temperature: d.weather.temperature_c ?? 0,
        irradiance: d.weather.irradiance_wpm2 ?? 0,
      };
      setChartData((prev) => [...prev.slice(-47), point]);
    }
  }, [dashQuery.data]);

  // Also backfill chart history from the readings history endpoint when
  // available, so the chart shows real historical points instead of nothing.
  useEffect(() => {
    readingService.getHistory(48).then((res) => {
      if (!res?.data?.length) return;
      const points: ChartDataPoint[] = res.data
        .map((r: Record<string, unknown>) => ({
          time: r.recorded_at ? new Date(String(r.recorded_at)).toLocaleTimeString() : '',
          power: Number(r.power ?? 0),
          voltage: Number(r.voltage ?? 0),
          current: Number(r.current ?? 0),
          temperature: Number(r.temperature ?? 0),
          irradiance: Number(r.irradiance ?? 0),
        }))
        .slice(-48);
      setChartData(points);
    }).catch(() => {
      /* no backend data yet — chart stays empty until data arrives */
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        {dashQuery.isFetching && (
          <span className="text-xs text-gray-400">Refreshing...</span>
        )}
      </div>

      {dashQuery.isError && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 text-sm text-red-700 dark:text-red-300">
          Could not connect to backend. No data to display.
        </div>
      )}

      <PlantOverview data={dashQuery.data} isLoading={dashQuery.isLoading} />
      <PowerChart data={chartData} />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <WeatherWidget />
        <RecentAlerts />
        <SystemStatusCard />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PlantHeatmap />
        <NotificationPanel />
      </div>
    </div>
  );
}
