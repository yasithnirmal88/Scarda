import { PlantOverview } from '../components/dashboard/PlantOverview';
import { WeatherWidget } from '../components/dashboard/WeatherWidget';
import { RecentAlerts } from '../components/dashboard/RecentAlerts';
import { SystemStatusCard } from '../components/dashboard/SystemStatusCard';
import { NotificationPanel } from '../components/dashboard/NotificationPanel';
import { PowerChart } from '../components/charts/PowerChart';
import { PlantHeatmap } from '../components/heatmap/PlantHeatmap';
import { generateMockChartData } from '../mock/fakeData';

const chartData = generateMockChartData();

export function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      <PlantOverview />
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
