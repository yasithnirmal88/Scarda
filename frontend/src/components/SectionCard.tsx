import type { Section } from '../types';

interface SectionCardProps {
  section: Section;
}

export function SectionCard({ section }: SectionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold text-lg">{section.name}</h3>
      <p className="text-sm text-gray-500">{section.description || 'No description'}</p>
      <p className="text-xs text-gray-400 mt-2">ID: {section.id}</p>
    </div>
  );
}
