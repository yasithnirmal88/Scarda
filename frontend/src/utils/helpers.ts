export function formatPower(watts: number): string {
  if (watts >= 1_000_000) return `${(watts / 1_000_000).toFixed(2)} MW`;
  if (watts >= 1_000) return `${(watts / 1_000).toFixed(2)} kW`;
  return `${watts.toFixed(1)} W`;
}

export function formatEnergy(wattHours: number): string {
  if (wattHours >= 1_000_000) return `${(wattHours / 1_000_000).toFixed(2)} MWh`;
  if (wattHours >= 1_000) return `${(wattHours / 1_000).toFixed(2)} kWh`;
  return `${wattHours.toFixed(1)} Wh`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDateTime(iso: string): string {
  return `${formatDate(iso)} ${formatTime(iso)}`;
}

export function classNames(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
