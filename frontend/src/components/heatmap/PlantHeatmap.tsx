import { useQuery } from '@tanstack/react-query';
import { sectionService } from '../../services/sectionService';
import type { Section } from '../../types';
import { HealthBadge } from '../common/HealthBadge';

export function PlantHeatmap() {
  // Sections come from the backend (which reflects the live provider plant).
  const { data: sections = [] } = useQuery<Section[]>(({
    queryKey: ['sections'],
    queryFn: sectionService.getAll,
    staleTime: 60_000,
  }) as never);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Plant Overview
      </h3>
      <div className="grid grid-cols-2 gap-3">
        {sections.map((section) => (
          <div
            key={section.id}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {section.name}
              </span>
              <HealthBadge status={section.status} />
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {section.inverterCount} inverters — {section.stringCount} strings
            </div>
            <div className="mt-2 grid grid-cols-3 gap-1">
              {Array.from({ length: 9 }, (_, i) => (
                <div
                  key={i}
                  className={`h-6 rounded text-[10px] flex items-center justify-center font-medium ${
                    section.status === 'healthy'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
                      : section.status === 'warning'
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
                  }`}
                >
                  INV{i + 1}
                </div>
              ))}
            </div>
          </div>
        ))}
        {sections.length === 0 && (
          <div className="col-span-2 text-sm text-gray-400">
            No section data from backend yet.
          </div>
        )}
      </div>
    </div>
  );
}
