import { STATUS_COLORS } from '../../utils/constants';
import { classNames } from '../../utils/helpers';

interface HealthBadgeProps {
  status: string;
  label?: string;
}

export function HealthBadge({ status, label }: HealthBadgeProps) {
  return (
    <span
      className={classNames(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        STATUS_COLORS[status] || STATUS_COLORS.offline,
      )}
    >
      <span className={classNames(
        'w-1.5 h-1.5 rounded-full mr-1.5',
        status === 'healthy' || status === 'online' || status === 'active' ? 'bg-current' :
        status === 'warning' ? 'bg-current' :
        status === 'critical' || status === 'error' ? 'bg-current' :
        'bg-current',
      )} />
      {label || status}
    </span>
  );
}
