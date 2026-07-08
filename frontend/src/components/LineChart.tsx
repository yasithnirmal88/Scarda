import {
  LineChart as RechartsChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const data = [
  { time: '00:00', power: 0 },
  { time: '04:00', power: 200 },
  { time: '08:00', power: 1800 },
  { time: '12:00', power: 2400 },
  { time: '16:00', power: 1600 },
  { time: '20:00', power: 400 },
  { time: '24:00', power: 0 },
];

export function LineChart() {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold mb-2">Power Output</h3>
      <ResponsiveContainer width="100%" height={200}>
        <RechartsChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Line type="monotone" dataKey="power" stroke="#3b82f6" />
        </RechartsChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">Placeholder chart</p>
    </div>
  );
}
