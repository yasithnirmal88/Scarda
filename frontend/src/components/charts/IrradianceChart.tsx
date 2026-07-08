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

interface IrradianceChartProps {
  data: ChartDataPoint[];
}

export function IrradianceChart({ data }: IrradianceChartProps) {
  const { isDark } = useTheme();
  const stroke = isDark ? '#6b7280' : '#9ca3af';

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="irrGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#eab308" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={stroke} />
        <XAxis dataKey="time" stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} />
        <YAxis stroke={stroke} tick={{ fill: stroke, fontSize: 11 }} unit=" W/m²" />
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
          dataKey="irradiance"
          stroke="#eab308"
          fill="url(#irrGrad)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
