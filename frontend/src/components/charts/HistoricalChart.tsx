import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '../../hooks/useTheme';

interface HistoricalData {
  date: string;
  value: number;
}

interface HistoricalChartProps {
  data: HistoricalData[];
  dataKey?: string;
  color?: string;
  title?: string;
}

export function HistoricalChart({
  data,
  dataKey = 'value',
  color = '#f59e0b',
  title,
}: HistoricalChartProps) {
  const { isDark } = useTheme();
  const stroke = isDark ? '#6b7280' : '#9ca3af';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      {title && (
        <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={stroke} />
          <XAxis dataKey="date" stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} />
          <YAxis stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: isDark ? '#1f2937' : '#fff',
              border: `1px solid ${stroke}`,
              borderRadius: 8,
              color: isDark ? '#fff' : '#111',
            }}
          />
          <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
