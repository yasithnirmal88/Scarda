import { useEffect, useState } from 'react';
import type { Section } from '../types';
import { sectionService } from '../services/sectionService';
import { HealthBadge } from '../components/common/HealthBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function Sections() {
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    sectionService.getAll().then((data) => {
      setSections(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Sections</h1>
      <div className="grid gap-4">
        {sections.map((section) => (
          <div
            key={section.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{section.name}</h3>
                <p className="text-sm text-gray-500">
                  {section.inverterCount} inverters — {section.stringCount} strings
                </p>
              </div>
              <HealthBadge status={section.status} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
