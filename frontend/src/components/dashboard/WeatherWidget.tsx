import { CloudSun, Thermometer, Wind, Droplets, Loader } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { weatherService } from '../../services/weatherService';

export function WeatherWidget() {
  const { data: w, isLoading, isError } = useQuery({
    queryKey: ['weather'],
    queryFn: weatherService.getCurrent,
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 flex items-center justify-center h-40">
        <Loader className="animate-spin text-gray-400" size={20} />
      </div>
    );
  }

  if (isError || !w) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
        <p className="text-sm text-gray-500 dark:text-gray-400">Weather data unavailable</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Weather
      </h3>
      <div className="flex items-center gap-4 mb-4">
        <div className="p-3 rounded-full bg-solar-50 dark:bg-solar-900/30">
          <CloudSun size={28} className="text-solar-600 dark:text-solar-400" />
        </div>
        <div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{w.temperature}°C</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{w.condition}</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Thermometer size={14} />
          <span>Feels {w.feelsLike}°C</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Wind size={14} />
          <span>{w.windSpeed} km/h</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Droplets size={14} />
          <span>{w.humidity}%</span>
        </div>
      </div>
    </div>
  );
}
