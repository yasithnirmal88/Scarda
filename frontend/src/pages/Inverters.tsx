import { InverterCard } from '../components/InverterCard';
import type { Inverter } from '../types';

const placeholderInverters: Inverter[] = Array.from({ length: 9 }, (_, i) => ({
  id: i + 1,
  section_id: 1,
  name: `INV-${String(i + 1).padStart(3, '0')}`,
  model_number: 'SUN2000-50KTL',
  status: i === 5 ? 'error' : i === 8 ? 'offline' : 'online',
}));

export function Inverters() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Inverters</h2>
      <p className="text-gray-500">This page will display inverters.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {placeholderInverters.map((inv) => (
          <InverterCard key={inv.id} inverter={inv} />
        ))}
      </div>
    </div>
  );
}
