import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '../../hooks/useTheme';
import type { ChartDataPoint } from '../../types';

interface PowerChartProps {
  data: ChartDataPoint[];
}

export function PowerChart({ data }: PowerChartProps) {
  const { isDark } = useTheme();
  const stroke = isDark ? '#6b7280' : '#9ca3af';
  const fill = isDark ? '#1f2937' : '#f3f4f6';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Power Output
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="powerGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={stroke} />
          <XAxis dataKey="time" stroke={stroke} tick={{ fill: stroke, fontSize: 12 }} />
          <YAxis stroke={stroke} tick={{ fill: stroke, fontSize: 12 }} unit=" kW" />
          <Tooltip
            contentStyle={{
              backgroundColor: isDark ? '#1f2937' : '#fff',
              border: `1px solid ${stroke}`,
              borderRadius: 8,
              color: isDark ? '#fff' : '#111',
            }}
          />
          <Area
            type="monotone"
            dataKey="power"
            stroke="#f59e0b"
            fill="url(#powerGrad)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
