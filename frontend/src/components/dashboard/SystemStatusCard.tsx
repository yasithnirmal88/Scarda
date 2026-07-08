import { HealthBadge } from '../common/HealthBadge';
import { mockSections } from '../../mock/mockSections';

export function SystemStatusCard() {
  const total = mockSections.length;
  const healthy = mockSections.filter((s) => s.status === 'healthy').length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        System Status
      </h3>
      <div className="space-y-3">
        {mockSections.map((section) => (
          <div key={section.id} className="flex items-center justify-between">
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {section.name}
            </span>
            <HealthBadge status={section.status} />
          </div>
        ))}
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-300">
            {healthy}/{total} sections healthy
          </span>
        </div>
      </div>
    </div>
  );
}
