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
import { generateMockChartData } from '../mock/fakeData';
import type { ChartDataPoint } from '../types';
import { useState, useEffect } from 'react';

const REFRESH_INTERVAL = 30_000;

export function Dashboard() {
  const [chartData, setChartData] = useState<ChartDataPoint[]>(() => generateMockChartData());

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
          Could not connect to backend. Using mock data.
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
