import { SectionCard } from '../components/SectionCard';
import type { Section } from '../types';

const placeholderSections: Section[] = [
  { id: 1, name: 'Section A', description: 'North field array' },
  { id: 2, name: 'Section B', description: 'East field array' },
  { id: 3, name: 'Section C', description: 'South field array' },
  { id: 4, name: 'Section D', description: 'West field array' },
];

export function Sections() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Sections</h2>
      <p className="text-gray-500">This page will display plant sections.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {placeholderSections.map((s) => (
          <SectionCard key={s.id} section={s} />
        ))}
      </div>
    </div>
  );
}
