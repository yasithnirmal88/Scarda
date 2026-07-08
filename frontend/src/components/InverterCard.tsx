import type { Inverter } from '../types';

interface InverterCardProps {
  inverter: Inverter;
}

export function InverterCard({ inverter }: InverterCardProps) {
  const statusColor =
    inverter.status === 'online'
      ? 'text-green-600'
      : inverter.status === 'error'
        ? 'text-red-600'
        : 'text-gray-400';

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">{inverter.name}</h3>
        <span className={`text-sm font-medium ${statusColor}`}>{inverter.status}</span>
      </div>
      <p className="text-sm text-gray-500">{inverter.model_number || 'N/A'}</p>
    </div>
  );
}
