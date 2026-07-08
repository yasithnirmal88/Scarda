import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '../../hooks/useTheme';
import type { ChartDataPoint } from '../../types';

interface EfficiencyChartProps {
  data: ChartDataPoint[];
}

export function EfficiencyChart({ data }: EfficiencyChartProps) {
  const { isDark } = useTheme();
  const stroke = isDark ? '#6b7280' : '#9ca3af';

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={stroke} />
        <XAxis dataKey="time" stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} />
        <YAxis stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} unit=" %" domain={[80, 100]} />
        <Tooltip
          contentStyle={{
            backgroundColor: isDark ? '#1f2937' : '#fff',
            border: `1px solid ${stroke}`,
            borderRadius: 8,
            color: isDark ? '#fff' : '#111',
          }}
        />
        <Line type="monotone" dataKey="efficiency" stroke="#8b5cf6" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
